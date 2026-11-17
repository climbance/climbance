"""A started card's state past its ladder, and the next spaced check or recall
it waits for: `log.md`, Card states and The template schedule."""

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from enum import StrEnum

from fsrs import Rating
from pydantic import BaseModel

from climb.knowledge.schedule import Review
from climb.ladder import CardState, Rung, card_state
from climb.schema import Attempt, Card, CardRun, Problem, RecallAttempt
from climb.template_schedule import check, due, recall_rating, reviews


class NextKind(StrEnum):
    CHECK = "check"
    RECALL = "recall"


class Next(BaseModel):
    """The spaced check a template waits for, or a graduated card's next due
    recall. `owed` is the check's alone."""

    kind: NextKind
    template_id: str
    opens: datetime
    owed: datetime | None = None


def reading(
    card: Card,
    run: CardRun | None,
    rungs: Sequence[Rung],
    attempts: Sequence[Attempt],
    problems: Mapping[str, Problem],
    recalls: Sequence[RecallAttempt],
) -> tuple[CardState, Next | None]:
    state = card_state(run is not None, rungs)
    if run is None or state is CardState.NOT_STARTED:
        return state, None
    if state is CardState.CONSOLIDATING:
        past, waits, _ = _past_ladder(card, run, rungs, attempts, problems, recalls)
        return past, waits
    # a graduated card no longer reads the ladder, so the rungs a later problem
    # added are left out: `log.md`, Card states
    unsolved = [rung for rung in rungs if rung.required and not rung.solved]
    held = [rung for rung in rungs if rung not in unsolved]
    if not any(rung.required for rung in held):
        return state, None
    past, waits, graduated = _past_ladder(card, run, held, attempts, problems, recalls)
    if graduated is None or any(
        rung.joined is None or rung.joined <= graduated for rung in unsolved
    ):
        return state, None
    return past, waits


def _past_ladder(
    card: Card,
    run: CardRun,
    rungs: Sequence[Rung],
    attempts: Sequence[Attempt],
    problems: Mapping[str, Problem],
    recalls: Sequence[RecallAttempt],
) -> tuple[CardState, Next | None, datetime | None]:
    """Consolidating, graduated or lapsed once every required rung is solved,
    with when the card first graduated."""
    first: datetime | None = None
    found = reviews(recalls, attempts, problems)
    recallable = [one.id for one in card.templates if one.cases]
    probe = _probe_solved(run, attempts, problems)
    pending = {template: _consolidated(run, rungs, attempts) for template in recallable}
    graduated = False
    while True:
        passed = {t: _passed_check(t, at, recalls, found.get(t, [])) for t, at in pending.items()}
        if any(at is None for at in passed.values()) or (not graduated and probe is None):
            waiting = [t for t, at in passed.items() if at is None]
            state = CardState.LAPSED if graduated else CardState.CONSOLIDATING
            return state, _next_check(waiting, found), first
        moments = [at for at in passed.values() if at is not None]
        moment: datetime = max(moments + ([probe] if probe else []))
        graduated = True
        first = first or moment
        lapsed = _lapses(recallable, found, after=moment)
        if not lapsed:
            return CardState.GRADUATED, _next_recall(recallable, found), first
        pending = lapsed


def _consolidated(run: CardRun, rungs: Iterable[Rung], attempts: Iterable[Attempt]) -> datetime:
    """The solve of the last required rung, each rung's first since the run."""
    firsts: dict[str, datetime] = {}
    for one in attempts:
        if one.solved_unaided and one.finished_at >= run.started_at:
            seen = firsts.get(one.problem_id)
            firsts[one.problem_id] = one.finished_at if seen is None else min(seen, one.finished_at)
    return max(firsts[rung.problem.id] for rung in rungs if rung.required)


def _probe_solved(
    run: CardRun, attempts: Iterable[Attempt], problems: Mapping[str, Problem]
) -> datetime | None:
    probed = {one.problem_id for one in run.probes}
    return min(
        (
            one.finished_at
            for one in attempts
            if one.problem_id in probed
            and one.solved_unaided
            and one.finished_at >= run.started_at
            and not problems[one.problem_id].defective
        ),
        default=None,
    )


def _passed_check(
    template: str, after: datetime, recalls: Iterable[RecallAttempt], found: Sequence[Review]
) -> datetime | None:
    """The first recall rated Good after `after`, once the check read from the
    reviews before it had opened."""
    for recall in sorted(recalls, key=lambda one: one.created_at):
        if recall.template_id != template or recall.created_at <= after:
            continue
        if recall_rating(recall) != Rating.Good:
            continue
        window = check([one for one in found if one.at < recall.created_at])
        if window is not None and recall.created_at >= window.opens:
            return recall.created_at
    return None


def _lapses(
    recallable: Iterable[str], found: Mapping[str, Sequence[Review]], *, after: datetime
) -> dict[str, datetime]:
    """Each template rated Again since `after`, from its first such review."""
    lapsed: dict[str, datetime] = {}
    for template in recallable:
        failed = [
            one.at
            for one in found.get(template, [])
            if one.at > after and one.rating == Rating.Again
        ]
        if failed:
            lapsed[template] = min(failed)
    return lapsed


def _next_check(waiting: Iterable[str], found: Mapping[str, Sequence[Review]]) -> Next | None:
    windows = [(t, w) for t in waiting if (w := check(found.get(t, []))) is not None]
    if not windows:
        return None
    template, window = min(windows, key=lambda one: one[1].opens)
    return Next(kind=NextKind.CHECK, template_id=template, opens=window.opens, owed=window.owed)


def _next_recall(recallable: Iterable[str], found: Mapping[str, Sequence[Review]]) -> Next | None:
    dues = [(t, at) for t in recallable if (at := due(found.get(t, []))) is not None]
    if not dues:
        return None
    template, at = min(dues, key=lambda one: one[1])
    return Next(kind=NextKind.RECALL, template_id=template, opens=at)
