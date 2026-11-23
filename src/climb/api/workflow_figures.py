"""The workflow page's figures, read from the store on each load:
`web-app/pages/author/workflow/README.md`."""

from collections.abc import Sequence
from datetime import date, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel
from sqlalchemy import Date, cast, func, literal, select, union_all

from climb.attempt_claims import claimable, standing_attempt_claims
from climb.calls.table import calls
from climb.cards import CardStore
from climb.difficulty import standing_correction
from climb.judgements import ItemStore
from climb.judging import stale, stale_key_lines
from climb.keylines import KeyLineStore
from climb.log import AttemptLog, FeedbackLog, RetirementRequestLog
from climb.log.table import attempt_claims, diagnoses, run_faults
from climb.matches import MatchLog, unsettled
from climb.matches.table import template_matches
from climb.mutant_diagnoses.table import mutant_diagnoses
from climb.outcomes.table import site_outcomes
from climb.ratings import CorrectionLog, RatingLog
from climb.ratings.table import difficulty_draws
from climb.schema import Client, Problem, RetirementReason, RunKind
from climb.solution_claims import load_problems
from climb.solution_claims.table import solution_claims
from climb.solutions import SolutionLog
from climb.storage import Database
from climb.trials.table import trials

PERIOD_DAYS = 30
# the latest faults the page lists with their detail
LATEST_FAULTS = 10


class Pass(StrEnum):
    """The command that clears what waits, as the author runs it."""

    CLAIM = "claim --by-hand"
    MATCH = "match --by-hand"
    DIFFICULTY = "difficulty judge"
    JUDGE = "judge build"
    FILL = "fill build"


class WaitingPass(BaseModel):
    command: Pass
    # None where no correction stands, so `difficulty judge` cannot run
    count: int | None


class RequestRow(BaseModel):
    created_at: datetime
    problem_id: str
    title: str
    reason: RetirementReason
    note: str
    waits: bool


class FeedbackRow(BaseModel):
    created_at: datetime
    client: Client
    page: str
    note: str


class FaultDay(BaseModel):
    day: date
    counts: dict[RunKind, int]


class FaultRow(BaseModel):
    created_at: datetime
    kind: RunKind
    detail: str


class SpendRow(BaseModel):
    part: str
    calls: int
    cost: float


class WorkflowFigures(BaseModel):
    period_days: int
    waiting: list[WaitingPass]
    requests: list[RequestRow]
    feedback: list[FeedbackRow]
    fault_days: list[FaultDay]
    faults: list[FaultRow]
    spend: list[SpendRow]
    uncosted: int


def workflow_figures(root: Database, author_id: str, now: datetime) -> WorkflowFigures:
    since = now - timedelta(days=PERIOD_DAYS)
    problems = load_problems(root)
    titles = {one.id: one for one in problems}
    requests = sorted(
        RetirementRequestLog(root).all(),
        key=lambda one: (not titles[one.problem_id].served, -one.created_at.timestamp()),
    )
    fault_days, faults = _faults(root, since)
    spend, uncosted = _spend(root, since)
    return WorkflowFigures(
        period_days=PERIOD_DAYS,
        waiting=_waiting(root, author_id, problems),
        requests=[
            RequestRow(
                created_at=one.created_at,
                problem_id=one.problem_id,
                title=titles[one.problem_id].title,
                reason=one.reason,
                note=one.note,
                waits=titles[one.problem_id].served,
            )
            for one in requests
        ],
        feedback=[
            FeedbackRow(created_at=one.created_at, client=one.client, page=one.page, note=one.note)
            for one in reversed(FeedbackLog(root).all())
        ],
        fault_days=fault_days,
        faults=faults,
        spend=spend,
        uncosted=uncosted,
    )


def _waiting(root: Database, author_id: str, problems: Sequence[Problem]) -> list[WaitingPass]:
    by_id = {one.id: one for one in problems}
    log = AttemptLog(root)
    claim = claimable(
        log.attempts(author_id),
        by_id,
        standing_attempt_claims(log.claims(author_id)),
        user_id=author_id,
    )
    cards = CardStore(root).all()
    questions = unsettled(cards, problems, SolutionLog(root).solutions(), MatchLog(root).matches())
    correction = standing_correction(CorrectionLog(root).all())
    unrated = None
    if correction is not None:
        rated = {
            one.problem_id for one in RatingLog(root).all() if one.correction_id == correction.id
        }
        unrated = sum(1 for one in problems if one.served and one.id not in rated)
    return [
        WaitingPass(command=Pass.CLAIM, count=len(claim)),
        # a question is a canonical against one card; the page counts canonicals
        WaitingPass(command=Pass.MATCH, count=len({one.solution.id for one in questions})),
        WaitingPass(command=Pass.DIFFICULTY, count=unrated),
        WaitingPass(command=Pass.JUDGE, count=len(stale(cards, ItemStore(root).all()))),
        WaitingPass(command=Pass.FILL, count=len(stale_key_lines(cards, KeyLineStore(root).all()))),
    ]


def _faults(root: Database, since: datetime) -> tuple[list[FaultDay], list[FaultRow]]:
    day = cast(func.timezone("UTC", run_faults.c.created_at), Date).label("day")
    recent = run_faults.c.created_at >= since
    with root.connect() as conn:
        counted = conn.execute(
            select(day, run_faults.c.kind, func.count())
            .where(recent)
            .group_by(day, run_faults.c.kind)
        ).all()
        latest = conn.execute(
            select(run_faults.c.created_at, run_faults.c.kind, run_faults.c.detail)
            .where(recent)
            .order_by(run_faults.c.created_at.desc(), run_faults.c.appended.desc())
            .limit(LATEST_FAULTS)
        ).all()
    days: dict[date, dict[RunKind, int]] = {}
    for one, kind, n in counted:
        days.setdefault(one, dict.fromkeys(RunKind, 0))[RunKind(kind)] = n
    return (
        [FaultDay(day=one, counts=days[one]) for one in sorted(days, reverse=True)],
        [FaultRow(created_at=at, kind=RunKind(kind), detail=detail) for at, kind, detail in latest],
    )


UNCITED = "uncited"


def _spend(root: Database, since: datetime) -> tuple[list[SpendRow], int]:
    # the part is read from the record citing the call: `cli/calls.md`
    cited = union_all(
        select(site_outcomes.c.call_id, ("generation · " + site_outcomes.c.site).label("part")),
        select(difficulty_draws.c.call_id, literal("difficulty · judge")),
        select(trials.c.call_id, literal("difficulty · panel")),
        select(attempt_claims.c.call_id, literal("classifier")),
        select(solution_claims.c.call_id, literal("classifier")),
        select(template_matches.c.call_id, literal("matcher")),
        select(diagnoses.c.call_id, literal("diagnoser")),
        select(mutant_diagnoses.c.call_id, literal("diagnoser")),
    ).subquery("cited")
    # one part per call, so a call two records cite is counted once
    parts = (
        select(cited.c.call_id, func.min(cited.c.part).label("part"))
        .where(cited.c.call_id.is_not(None))
        .group_by(cited.c.call_id)
        .subquery("parts")
    )
    part = func.coalesce(parts.c.part, UNCITED).label("part")
    query = (
        select(
            part,
            func.count(),
            func.coalesce(func.sum(calls.c.cost), 0.0),
            func.count().filter(calls.c.cost.is_(None)),
        )
        .select_from(calls.outerjoin(parts, parts.c.call_id == calls.c.id))
        .where(calls.c.created_at >= since)
        .group_by(part)
    )
    with root.connect() as conn:
        rows = conn.execute(query).all()
    spend = [SpendRow(part=name, calls=n, cost=cost) for name, n, cost, _ in rows]
    # the most first, and `uncited` last since no part owns it
    spend.sort(key=lambda one: (one.part == UNCITED, -one.cost, one.part))
    return spend, sum(row[3] for row in rows)
