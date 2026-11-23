"""The generation page's figures, computed from the records on each load:
`web-app/pages/author/generation/README.md`."""

from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta

from pydantic import BaseModel

from climb.matches import coverage
from climb.schema import (
    CallSite,
    Card,
    Draft,
    Gate,
    Problem,
    ProblemDifficulty,
    SiteOutcome,
    Solution,
    TemplateMatch,
    WritingState,
)

PERIOD_DAYS = 30


class Stop(BaseModel):
    """Where the period's writings that did not land stopped: a site's gate, a
    gate no site answered for, or the state a held draft waits at."""

    site: CallSite | None
    gate: Gate | None
    held_at: WritingState | None
    writings: int


class DraftCount(BaseModel):
    state: WritingState
    drafts: int
    # a rejected draft waits for nothing, so it carries no age
    oldest_days: int | None


class CorpusRow(BaseModel):
    card_slug: str
    template_slug: str
    optional: bool
    counts: dict[ProblemDifficulty, int]
    # a served problem with neither a rating nor the generator's label
    unlabelled: int
    retired: int
    gap: bool


class GenerationFigures(BaseModel):
    period_days: int
    writings: int
    landed: int
    spend: float | None
    spend_per_landed: float | None
    uncosted: int
    stops: list[Stop]
    drafts: list[DraftCount]
    corpus: list[CorpusRow]
    # problems written for a technique, on no template's row
    untemplated: int


def generation_figures(
    outcomes: Sequence[SiteOutcome],
    drafts: Sequence[Draft],
    problems: Sequence[Problem],
    solutions: Iterable[Solution],
    matches: Iterable[TemplateMatch],
    cards: Iterable[Card],
    now: datetime,
) -> GenerationFigures:
    by_writing: dict[str, list[SiteOutcome]] = {}
    for one in outcomes:
        by_writing.setdefault(one.writing_id, []).append(one)
    since = now - timedelta(days=PERIOD_DAYS)
    # a replay's writing has no generator outcome, and lands nothing
    writings = {
        writing_id: left
        for writing_id, left in by_writing.items()
        if any(one.site is CallSite.GENERATOR for one in left)
        and min(one.created_at for one in left) >= since
    }
    landed = {w for w, left in writings.items() if any(one.problem_id for one in left)}
    paid = [one for left in writings.values() for one in left]
    costs = [one.cost for one in paid if one.cost is not None]
    spend = sum(costs) if costs else None
    held = {one.id: one for one in drafts}
    stops = Counter(
        stopped(left, held.get(writing_id))
        for writing_id, left in writings.items()
        if writing_id not in landed
    )
    return GenerationFigures(
        period_days=PERIOD_DAYS,
        writings=len(writings),
        landed=len(landed),
        spend=spend,
        spend_per_landed=spend / len(landed) if spend is not None and landed else None,
        uncosted=len(paid) - len(costs),
        stops=[
            Stop(site=site, gate=gate, held_at=state, writings=count)
            for (site, gate, state), count in sorted(stops.items(), key=ranked)
        ],
        drafts=drafts_now(drafts, by_writing, now),
        corpus=corpus(cards, problems, solutions, matches),
        untemplated=sum(1 for one in problems if one.target_template_id is None),
    )


type Where = tuple[CallSite | None, Gate | None, WritingState | None]


def ranked(item: tuple[Where, int]) -> tuple[int, bool, str, str, str]:
    # the most first, and on a tie a gate before a held state
    (site, gate, state), count = item
    return (-count, state is not None, site or "", gate or "", state or "")


def stopped(left: Sequence[SiteOutcome], draft: Draft | None) -> Where:
    gated = [one for one in left if one.gate is not None]
    if gated:
        last = max(gated, key=lambda one: one.created_at)
        return last.site, last.gate, None
    if draft is None:
        return None, None, None
    # `unexercised` is read from the draft: no site's answer raised it
    if draft.state is WritingState.REJECTED:
        return None, draft.gate, None
    return None, None, draft.state


def drafts_now(
    drafts: Sequence[Draft], by_writing: dict[str, list[SiteOutcome]], now: datetime
) -> list[DraftCount]:
    order = list(WritingState)
    counts = Counter(one.state for one in drafts)
    begun: dict[WritingState, datetime] = {}
    for one in drafts:
        left = by_writing.get(one.id)
        if one.state is WritingState.REJECTED or not left:
            continue
        first = min(record.created_at for record in left)
        begun[one.state] = min(begun.get(one.state, first), first)
    return [
        DraftCount(
            state=state,
            drafts=counts[state],
            oldest_days=(now - begun[state]).days if state in begun else None,
        )
        for state in sorted(counts, key=order.index)
    ]


def corpus(
    cards: Iterable[Card],
    problems: Sequence[Problem],
    solutions: Iterable[Solution],
    matches: Iterable[TemplateMatch],
) -> list[CorpusRow]:
    written: dict[str, list[Problem]] = {}
    for one in problems:
        if one.target_template_id is not None:
            written.setdefault(one.target_template_id, []).append(one)
    rows: list[CorpusRow] = []
    for one in coverage(sorted(cards, key=lambda card: card.slug), problems, solutions, matches):
        mine = written.get(one.template_id, [])
        served = [problem for problem in mine if problem.served]
        labels = Counter(problem.difficulty for problem in served)
        rows.append(
            CorpusRow(
                card_slug=one.card_slug,
                template_slug=one.template_slug,
                optional=one.optional,
                counts={label: labels[label] for label in ProblemDifficulty},
                unlabelled=labels[None],
                retired=len(mine) - len(served),
                gap=one.gap,
            )
        )
    return rows
