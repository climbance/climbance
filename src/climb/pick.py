"""The one act the board serves: `flows.md`, The pick."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from fsrs import Rating
from pydantic import BaseModel

from climb.graduation import Next, NextKind
from climb.knowledge.schedule import Review
from climb.ladder import CardState, Rung, next_rung
from climb.schema import Act, Attempt, Card, CardRun, FailureMode, Problem, Rank
from climb.template_schedule import recall_probability

CAP = 2  # cards in flight
# each says the solver held the form, so the failure aims nothing
HELD = {FailureMode.SYNTAX, FailureMode.SPEED}


class Pick(BaseModel):
    rank: Rank
    act: Act
    card_slug: str
    template_id: str | None = None  # absent on a probe and a new card
    problem_id: str | None = None  # a sitting's alone
    probe: bool = False  # a probe ranks with the rungs, and reads apart from them


@dataclass(frozen=True, slots=True)
class CardReading:
    """One card as the pick reads it, folded as the cards list folds it."""

    card: Card
    depth: int
    locked: bool
    run: CardRun | None
    rungs: Sequence[Rung]
    state: CardState
    next: Next | None
    execution: float | None = None  # the card's technique's, unknown while absent


def in_flight(reading: CardReading, now: datetime) -> bool:
    if reading.state is CardState.ACQUIRING:
        return True
    return reading.state is CardState.CONSOLIDATING and _check_open(reading.next, now)


def pick(
    readings: Iterable[CardReading],
    reviews: Mapping[str, Sequence[Review]],
    problems: Iterable[Problem],
    attempts: Iterable[Attempt],
    labels: Mapping[str, FailureMode],
    now: datetime,
) -> Pick | None:
    found = offers(readings, reviews, problems, attempts, labels, now)
    return found[0] if found else None


def offers(
    readings: Iterable[CardReading],
    reviews: Mapping[str, Sequence[Review]],
    problems: Iterable[Problem],
    attempts: Iterable[Attempt],
    labels: Mapping[str, FailureMode],
    now: datetime,
) -> list[Pick]:
    """Every offer, first served first. `labels` holds each attempt's
    standing self-label, by attempt id."""
    readings, problems, attempts = list(readings), list(problems), list(attempts)
    offered: list[tuple[tuple[int, float, int, float, str], Pick]] = []

    def offer(
        rank: Rank,
        reading: CardReading,
        act: Act,
        *,
        template_id: str | None = None,
        problem_id: str | None = None,
        probe: bool = False,
    ) -> None:
        template = template_id
        chance = recall_probability(reviews.get(template, []), now) if template else None
        # an unknown execution reading ranks first, as the least practised
        known = -1.0 if reading.execution is None else reading.execution
        key = (rank, 1.0 if chance is None else chance, reading.depth, known, reading.card.slug)
        chosen = Pick(
            rank=rank,
            act=act,
            card_slug=reading.card.slug,
            template_id=template_id,
            problem_id=problem_id,
            probe=probe,
        )
        offered.append((key, chosen))

    owed = False
    for reading in readings:
        upcoming, state = reading.next, reading.state
        if state in (CardState.CONSOLIDATING, CardState.LAPSED) and _check_open(upcoming, now):
            assert upcoming is not None
            late = upcoming.owed is not None and now >= upcoming.owed
            owed = owed or late
            rank = Rank.OWED_CHECK if late else Rank.OPEN_CHECK
            offer(rank, reading, Act.RECALL, template_id=upcoming.template_id)
        elif state is CardState.GRADUATED and upcoming is not None and now >= upcoming.opens:
            template = upcoming.template_id
            aimed = _missed(template, reviews.get(template, []), problems, attempts, labels)
            problem = None if aimed else _unsolved(template, problems, attempts)
            act = Act.SITTING if problem else Act.RECALL
            offer(Rank.DUE_REVIEW, reading, act, template_id=template, problem_id=problem)
        elif state is CardState.ACQUIRING:
            rung = next_rung(reading.rungs)
            if rung is not None:
                offer(Rank.RUNG, reading, Act.SITTING, problem_id=rung.problem.id)
        if state is CardState.CONSOLIDATING and (probe := _probe(reading, problems, attempts)):
            offer(Rank.RUNG, reading, Act.SITTING, problem_id=probe, probe=True)

    flying = sum(in_flight(one, now) for one in readings)
    if flying < CAP and not owed:
        for reading in readings:
            if reading.state is CardState.NOT_STARTED and not reading.locked:
                offer(Rank.NEW_CARD, reading, Act.START)
    return [one for _, one in sorted(offered, key=lambda one: one[0])]


def _check_open(upcoming: Next | None, now: datetime) -> bool:
    return upcoming is not None and upcoming.kind is NextKind.CHECK and now >= upcoming.opens


def _missed(
    template: str,
    found: Sequence[Review],
    problems: Iterable[Problem],
    attempts: Iterable[Attempt],
    labels: Mapping[str, FailureMode],
) -> bool:
    """Whether the template's last review is a failed sitting that missed the
    form, which aims a recall before the next problem."""
    if not found or found[-1].rating != Rating.Again:
        return False
    written = {one.id for one in problems if one.target_template_id == template}
    # a sitting's review sits at its first submission; a failed recall has none
    first = next(
        (
            one
            for one in attempts
            if one.problem_id in written
            and one.sitting_id is not None
            and one.finished_at == found[-1].at
        ),
        None,
    )
    if first is None:
        return False
    ended = max(
        (one for one in attempts if one.sitting_id == first.sitting_id),
        key=lambda one: one.finished_at,
    )
    return labels.get(ended.id) not in HELD


def _solved(attempts: Iterable[Attempt]) -> set[str]:
    return {one.problem_id for one in attempts if one.solved_unaided}


def _unsolved(
    template: str, problems: Iterable[Problem], attempts: Iterable[Attempt]
) -> str | None:
    """A live problem written for the template that the user has not solved,
    one never attempted first."""
    attempts = list(attempts)
    solved, tried = _solved(attempts), {one.problem_id for one in attempts}
    written = sorted(
        (one for one in problems if one.target_template_id == template and one.served),
        key=lambda one: (one.id in tried, one.id),
    )
    return next((one.id for one in written if one.id not in solved), None)


def _probe(
    reading: CardReading, problems: Iterable[Problem], attempts: Iterable[Attempt]
) -> str | None:
    """The run's next unattempted probe, while no probe of the run is solved."""
    if reading.run is None:
        return None
    since = [one for one in attempts if one.finished_at >= reading.run.started_at]
    live = {one.id for one in problems if not one.defective}
    probed = [one.problem_id for one in reading.run.probes if one.problem_id in live]
    if set(probed) & _solved(since):
        return None
    tried = {one.problem_id for one in since}
    return next((one for one in probed if one not in tried), None)
