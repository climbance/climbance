"""A question's memory, replayed from its answers: `knowledge.md`, The
schedule."""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

from fsrs import Card, Rating, Scheduler

from climb.schema.knowledge import Answer, OpenGrade

# py-fsrs's defaults, fuzzing off. The snapshot publishes these, so every
# client replays with the same settings.
FSRS: dict[str, Any] = {
    "version": 6,
    "desired_retention": 0.9,
    "maximum_interval": 36500,
    "learning_steps_minutes": [1.0, 10.0],
    "relearning_steps_minutes": [10.0],
    "enable_fuzzing": False,
    "parameters": [
        0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001, 1.8722, 0.1666, 0.796,
        1.4835, 0.0614, 0.2629, 1.6483, 0.6014, 1.8729, 0.5425, 0.0912, 0.0658, 0.1542,
    ],
    "mastered_stability_days": 21,
}  # fmt: skip


class QuestionState(StrEnum):
    UNSEEN = "unseen"
    WEAK = "weak"
    DUE = "due"
    LEARNING = "learning"
    RETAINED = "retained"


@dataclass(frozen=True, slots=True)
class Review:
    at: datetime
    rating: Rating


@dataclass(frozen=True, slots=True)
class Memory:
    stability: float  # days
    difficulty: float
    due: datetime


def _minutes(values: Sequence[float]) -> tuple[timedelta, ...]:
    return tuple(timedelta(minutes=m) for m in values)


def scheduler(settings: dict[str, Any]) -> Scheduler:
    return Scheduler(
        parameters=settings["parameters"],
        desired_retention=settings["desired_retention"],
        learning_steps=_minutes(settings["learning_steps_minutes"]),
        relearning_steps=_minutes(settings["relearning_steps_minutes"]),
        maximum_interval=settings["maximum_interval"],
        enable_fuzzing=settings["enable_fuzzing"],
    )


SCHEDULER = scheduler(FSRS)
RETAINED_DAYS: float = FSRS["mastered_stability_days"]


GRADED = {
    OpenGrade.KNOWN: Rating.Good,
    OpenGrade.PARTIAL: Rating.Hard,
    OpenGrade.NONE: Rating.Again,
}


def rating(answer: Answer) -> Rating:
    if answer.grade is not None:
        return GRADED[answer.grade]
    if not answer.correct:
        return Rating.Again
    return Rating.Hard if answer.guess else Rating.Good


def history(answers: Iterable[Answer]) -> dict[str, list[Review]]:
    """Each question's reviews, in the order the user gave them."""
    reviews: dict[str, list[Review]] = defaultdict(list)
    for a in sorted(answers, key=lambda a: a.at):
        reviews[a.question_id].append(Review(a.at, rating(a)))
    return dict(reviews)


def fsrs_card(reviews: Sequence[Review], scheduler: Scheduler | None = None) -> Card | None:
    """py-fsrs's card after each review at its own moment, in order."""
    if not reviews:
        return None
    # a fixed id: py-fsrs otherwise sleeps a millisecond to mint one
    card = Card(card_id=0)
    for r in reviews:
        card, _ = (scheduler or SCHEDULER).review_card(card, r.rating, r.at)
    return card


def replay(reviews: Sequence[Review], scheduler: Scheduler | None = None) -> Memory | None:
    card = fsrs_card(reviews, scheduler)
    if card is None:
        return None
    assert card.stability is not None and card.difficulty is not None
    return Memory(card.stability, card.difficulty, card.due)


def passes(review: Review) -> bool:
    return review.rating == Rating.Good


def passed(reviews: Sequence[Review]) -> bool:
    return any(passes(r) for r in reviews)


def state(reviews: Sequence[Review], at: datetime) -> QuestionState:
    memory = replay(reviews)
    if memory is None:
        return QuestionState.UNSEEN
    if not passes(reviews[-1]):
        return QuestionState.WEAK
    if at >= memory.due:
        return QuestionState.DUE
    if memory.stability >= RETAINED_DAYS:
        return QuestionState.RETAINED
    return QuestionState.LEARNING


def servable(reviews: Sequence[Review], at: datetime) -> bool:
    memory = replay(reviews)
    return memory is None or at >= memory.due
