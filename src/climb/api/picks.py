"""The board's pick, gathered from the stores as the cards list is."""

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from climb.api.context import Root, UserId
from climb.attempt_claims import standing_attempt_claims
from climb.board.execution import execution
from climb.cards import CardStore
from climb.cards.graph import depths
from climb.graduation import reading
from climb.ladder import Ladder, ladder, met, unmet
from climb.log import AttemptLog, CardRunLog, RecallLog, latest_by_attempt
from climb.matches import MatchLog
from climb.pick import Act, CardReading, Rank, pick
from climb.schema import CardRun
from climb.solution_claims import load_problems
from climb.solutions import SolutionLog
from climb.template_schedule import reviews

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


@router.get("/pick")
def board_pick(root: Root, user_id: UserId) -> BoardPick | None:
    problems = load_problems(root)
    by_id = {one.id: one for one in problems}
    log = AttemptLog(root)
    attempts = log.attempts(user_id)
    standing = latest_by_attempt(log.self_labels(user_id))
    labels = {key: one.mode for key, one in standing.items()}
    read = execution(attempts, by_id, standing_attempt_claims(log.claims(user_id)), standing)
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
    chosen = pick(
        readings, reviews(recalls, attempts, by_id), problems, attempts, labels, datetime.now(UTC)
    )
    if chosen is None:
        return None
    card = next(one for one in cards if one.slug == chosen.card_slug)
    template = next((one for one in card.templates if one.id == chosen.template_id), None)
    problem = by_id.get(chosen.problem_id) if chosen.problem_id else None
    return BoardPick(
        rank=chosen.rank,
        act=chosen.act,
        probe=chosen.probe,
        card_slug=card.slug,
        card_title=card.title,
        technique=card.technique,
        template_slug=template.slug if template else None,
        template_title=template.title if template else None,
        problem_id=problem.id if problem else None,
        problem_title=problem.title if problem else None,
    )
