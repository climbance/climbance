"""The inbox's figures, read from the store on each load:
`web-app/pages/author/inbox/README.md`."""

from collections.abc import Sequence
from datetime import date, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel
from sqlalchemy import Date, cast, func, select

from climb.attempt_claims import claimable, standing_attempt_claims
from climb.cards import CardStore
from climb.difficulty import standing_correction
from climb.judgements import ItemStore
from climb.judging import stale, stale_key_lines
from climb.keylines import KeyLineStore
from climb.log import AttemptLog, FeedbackLog, RetirementRequestLog
from climb.log.table import run_faults
from climb.matches import MatchLog, unsettled
from climb.ratings import CorrectionLog, RatingLog
from climb.schema import Client, Problem, ProblemStatus, RetirementReason, RunKind
from climb.solution_claims import load_problems
from climb.solutions import SolutionLog
from climb.storage import Database

PERIOD_DAYS = 30
FEEDBACK_DAYS = 7
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
    status: ProblemStatus


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


class InboxFigures(BaseModel):
    period_days: int
    waiting: list[WaitingPass]
    # a request waits while its problem is still served
    waiting_requests: list[RequestRow]
    answered_requests: list[RequestRow]
    feedback: list[FeedbackRow]
    feedback_days: int
    feedback_recent: int
    fault_days: list[FaultDay]
    faults: list[FaultRow]


def inbox_figures(root: Database, author_id: str, now: datetime) -> InboxFigures:
    since = now - timedelta(days=PERIOD_DAYS)
    problems = load_problems(root)
    by_id = {one.id: one for one in problems}
    rows = _requests(root, by_id)
    feedback = list(reversed(FeedbackLog(root).all()))
    recent = now - timedelta(days=FEEDBACK_DAYS)
    fault_days, faults = _faults(root, since)
    return InboxFigures(
        period_days=PERIOD_DAYS,
        waiting=_waiting(root, author_id, problems),
        waiting_requests=[one for one in rows if by_id[one.problem_id].served],
        answered_requests=[one for one in rows if not by_id[one.problem_id].served],
        feedback=[
            FeedbackRow(created_at=one.created_at, client=one.client, page=one.page, note=one.note)
            for one in feedback
        ],
        feedback_days=FEEDBACK_DAYS,
        feedback_recent=sum(1 for one in feedback if one.created_at >= recent),
        fault_days=fault_days,
        faults=faults,
    )


def waiting_rows(root: Database, author_id: str) -> int:
    """The rows under the inbox's What waits that count something."""
    problems = load_problems(root)
    by_id = {one.id: one for one in problems}
    passes = sum(1 for one in _waiting(root, author_id, problems) if one.count)
    return passes + sum(
        1 for one in RetirementRequestLog(root).all() if by_id[one.problem_id].served
    )


def _requests(root: Database, by_id: dict[str, Problem]) -> list[RequestRow]:
    # newest first
    return [
        RequestRow(
            created_at=one.created_at,
            problem_id=one.problem_id,
            title=by_id[one.problem_id].title,
            reason=one.reason,
            note=one.note,
            status=by_id[one.problem_id].status,
        )
        for one in sorted(RetirementRequestLog(root).all(), key=lambda one: one.created_at)
    ][::-1]


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
