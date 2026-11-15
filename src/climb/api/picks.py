"""The board's pick, gathered from the stores as the cards list is, and the
prediction stored as the user takes it: `log.md`, Predictions."""

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from climb import template_schedule
from climb.api.context import Root, UserId
from climb.attempt_claims import standing_attempt_claims
from climb.board import execution as executed
from climb.cards import CardStore
from climb.cards.graph import depths
from climb.graduation import reading
from climb.ids import new_id
from climb.knowledge.schedule import Review
from climb.ladder import Ladder, ladder, met, unmet
from climb.log import AttemptLog, CardRunLog, PredictionLog, RecallLog, latest_by_attempt
from climb.matches import MatchLog
from climb.pick import CardReading, Pick, pick
from climb.schema import Act, Attempt, Card, CardRun, Prediction, Problem, Rank
from climb.solution_claims import load_problems
from climb.solutions import SolutionLog
from climb.template_schedule import recall_probability, reviews

router = APIRouter()


class BoardPick(BaseModel):
    """The pick, named as the board shows it."""

    rank: Rank
    act: Act
    probe: bool
    card_slug: str
    card_title: str
    technique: str  # the card's, which a sitting the pick opens is drilled for
    template_slug: str | None
    template_title: str | None
    problem_id: str | None
    problem_title: str | None


class Taken(BaseModel):
    """The pick the board showed, which the user took."""

    card_slug: str
    template_slug: str | None = None
    problem_id: str | None = None


@dataclass(frozen=True, slots=True)
class Gathered:
    chosen: Pick | None
    cards: list[Card]
    problems: dict[str, Problem]
    attempts: list[Attempt]
    runs: CardRunLog
    reviews: dict[str, list[Review]]
    execution: dict[str, tuple[int, float | None]]
    now: datetime


def _gathered(root: Root, user_id: str) -> Gathered:
    problems = load_problems(root)
    by_id = {one.id: one for one in problems}
    log = AttemptLog(root)
    attempts = log.attempts(user_id)
    standing = latest_by_attempt(log.self_labels(user_id))
    labels = {key: one.mode for key, one in standing.items()}
    read = executed.execution(
        attempts, by_id, standing_attempt_claims(log.claims(user_id)), standing
    )
    solutions, matches = SolutionLog(root).solutions(), MatchLog(root).matches()
    runs, recalls = CardRunLog(root), RecallLog(root).all(user_id)
    cards = CardStore(root).all()
    held: dict[str, tuple[CardRun | None, Ladder]] = {}
    for card in cards:
        run = runs.started(user_id, card.id)
        since = run.started_at if run else None
        held[card.slug] = (run, ladder(card, problems, solutions, matches, attempts, since=since))
    reached = {slug for slug, (run, found) in held.items() if met(run, found.rungs, attempts)}
    deep = depths(cards)
    readings: list[CardReading] = []
    for card in cards:
        run, found = held[card.slug]
        own = [one for one in recalls if one.card_id == card.id]
        state, upcoming = reading(card, run, found.rungs, attempts, by_id, own)
        readings.append(
            CardReading(
                card=card,
                depth=deep[card.slug],
                locked=run is None and bool(unmet(card, reached)),
                run=run,
                rungs=found.rungs,
                state=state,
                next=upcoming,
                execution=read.get(card.technique, (0, None))[1],
            )
        )
    found_reviews = reviews(recalls, attempts, by_id)
    now = datetime.now(UTC)
    chosen = pick(readings, found_reviews, problems, attempts, labels, now)
    return Gathered(chosen, cards, by_id, attempts, runs, found_reviews, read, now)


@router.get("/pick")
def board_pick(root: Root, user_id: UserId) -> BoardPick | None:
    found = _gathered(root, user_id)
    if found.chosen is None:
        return None
    card = next(one for one in found.cards if one.slug == found.chosen.card_slug)
    template = next((one for one in card.templates if one.id == found.chosen.template_id), None)
    problem = found.problems.get(found.chosen.problem_id) if found.chosen.problem_id else None
    return BoardPick(
        rank=found.chosen.rank,
        act=found.chosen.act,
        probe=found.chosen.probe,
        card_slug=card.slug,
        card_title=card.title,
        technique=card.technique,
        template_slug=template.slug if template else None,
        template_title=template.title if template else None,
        problem_id=problem.id if problem else None,
        problem_title=problem.title if problem else None,
    )


@router.post("/pick")
def taken(root: Root, user_id: UserId, body: Taken) -> Prediction:
    """Stores what the pick predicts as the user takes it, once per pick: a
    second take before any outcome returns the first prediction."""
    found = _gathered(root, user_id)
    chosen = found.chosen
    card = next((one for one in found.cards if chosen and one.slug == chosen.card_slug), None)
    template = (
        next((one for one in card.templates if chosen and one.id == chosen.template_id), None)
        if card
        else None
    )
    shown = (body.card_slug, body.template_slug, body.problem_id)
    current = (
        (card.slug, template.slug if template else None, chosen.problem_id)
        if card and chosen
        else None
    )
    # the board showed a pick that no longer stands, so its prediction would
    # be made about an act the schedule did not choose
    if chosen is None or card is None or current != shown:
        raise HTTPException(status_code=409, detail="the pick moved; reload the board")
    log = PredictionLog(root)
    pending = _pending(log.for_user(user_id), chosen, card, found)
    if pending is not None:
        return pending
    reviewed = found.reviews.get(chosen.template_id, []) if chosen.template_id else []
    prediction = Prediction(
        id=new_id(),
        created_at=found.now,
        user_id=user_id,
        rank=chosen.rank,
        act=chosen.act,
        card_id=card.id,
        template_id=chosen.template_id,
        problem_id=chosen.problem_id,
        probe=chosen.probe,
        recall_probability=recall_probability(reviewed, found.now) if reviewed else None,
        fsrs_settings=template_schedule.SETTINGS_HASH,
        execution=found.execution.get(card.technique, (0, None))[1],
        execution_settings=executed.SETTINGS_HASH,
    )
    log.append(prediction)
    return prediction


def _pending(
    held: list[Prediction], chosen: Pick, card: Card, found: Gathered
) -> Prediction | None:
    """The latest prediction about the same act that no outcome has met yet."""
    same = [
        one
        for one in held
        if (one.act, one.card_id, one.template_id, one.problem_id)
        == (chosen.act, card.id, chosen.template_id, chosen.problem_id)
    ]
    if not same:
        return None
    last = max(same, key=lambda one: one.created_at)
    if chosen.template_id:
        met = any(r.at > last.created_at for r in found.reviews.get(chosen.template_id, []))
    elif chosen.problem_id:
        met = any(
            a.problem_id == chosen.problem_id and a.finished_at > last.created_at
            for a in found.attempts
        )
    else:
        run = found.runs.started(last.user_id, card.id)
        met = run is not None and run.started_at > last.created_at
    return None if met else last
