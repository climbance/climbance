"""The spend page's figures, read from the call log on each load:
`web-app/pages/author/spend/README.md`."""

from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import func, literal, select, union_all

from climb.calls.table import calls
from climb.log.table import attempt_claims, diagnoses
from climb.matches.table import template_matches
from climb.mutant_diagnoses.table import mutant_diagnoses
from climb.outcomes.table import site_outcomes
from climb.ratings.table import difficulty_draws
from climb.solution_claims.table import solution_claims
from climb.storage import Database
from climb.trials.table import trials

PERIOD_DAYS = 30
UNCITED = "uncited"


class SpendRow(BaseModel):
    part: str
    calls: int
    cost: float


class SpendFigures(BaseModel):
    period_days: int
    spend: list[SpendRow]
    uncosted: int


def spend_figures(root: Database, now: datetime) -> SpendFigures:
    since = now - timedelta(days=PERIOD_DAYS)
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
    return SpendFigures(period_days=PERIOD_DAYS, spend=spend, uncosted=sum(row[3] for row in rows))
