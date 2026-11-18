"""Each template's memory for one user: `api/template-schedule.md`."""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from fsrs import Rating

from climb.ids import settings_hash
from climb.knowledge.schedule import FSRS, Review, fsrs_card, replay, scheduler
from climb.schema import Attempt, Hint, Problem, RecallAttempt

# the template settings, apart from the questions' though equal to them for now
SETTINGS = FSRS
SCHEDULER = scheduler(SETTINGS)
SETTINGS_HASH = settings_hash(SETTINGS)
CHECK_OPENS = 0.89
CHECK_OWED = 0.84
CHECK_FLOOR = timedelta(days=3)
DAY = timedelta(days=1)


@dataclass(frozen=True, slots=True)
class Check:
    opens: datetime
    owed: datetime


def recall_rating(recall: RecallAttempt) -> Rating:
    # typing back a form just read recalls nothing
    if not recall.verified or Hint.FORM in recall.hints:
        return Rating.Again
    return Rating.Hard if recall.hints else Rating.Good


def sitting_rating(attempts: Sequence[Attempt]) -> Rating:
    """Over one sitting's attempts, in the order they were submitted."""
    if attempts[0].solved_unaided:
        return Rating.Good
    return Rating.Hard if any(a.solved_unaided for a in attempts) else Rating.Again


def reviews(
    recalls: Iterable[RecallAttempt],
    attempts: Iterable[Attempt],
    problems: Mapping[str, Problem],
) -> dict[str, list[Review]]:
    """Each template's reviews, in time order. `flows.md` gives which sittings
    count."""
    out: dict[str, list[Review]] = defaultdict(list)
    for recall in recalls:
        out[recall.template_id].append(Review(recall.created_at, recall_rating(recall)))
    sittings: dict[str, list[Attempt]] = defaultdict(list)
    for attempt in attempts:
        if attempt.sitting_id is not None:
            sittings[attempt.sitting_id].append(attempt)
    for submitted in sittings.values():
        submitted.sort(key=lambda a: a.finished_at)
        problem = problems[submitted[0].problem_id]
        if problem.target_template_id is None or problem.defective:
            continue
        out[problem.target_template_id].append(
            Review(submitted[0].finished_at, sitting_rating(submitted))
        )
    return {template: sorted(found, key=lambda r: r.at) for template, found in out.items()}


def recall_probability(reviews: Sequence[Review], at: datetime) -> float | None:
    card = fsrs_card(reviews, SCHEDULER)
    return None if card is None else SCHEDULER.get_card_retrievability(card, at)


def due(reviews: Sequence[Review]) -> datetime | None:
    memory = replay(reviews, SCHEDULER)
    return None if memory is None else memory.due


def check(reviews: Sequence[Review]) -> Check | None:
    """The spaced check's window, read from the last review."""
    card = fsrs_card(reviews, SCHEDULER)
    if card is None or card.last_review is None:
        return None
    last = card.last_review

    # py-fsrs counts whole days since the last review
    def falls_to(probability: float) -> datetime:
        days = 0
        while SCHEDULER.get_card_retrievability(card, last + days * DAY) > probability:
            days += 1
        return last + days * DAY

    opens = max(falls_to(CHECK_OPENS), last + CHECK_FLOOR)
    return Check(opens, max(falls_to(CHECK_OWED), opens))
