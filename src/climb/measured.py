"""A user's measured rating, replayed from the user's cold sittings on every
read. `api/rating.md` gives the games, the periods and the scores read."""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict

from climb.glicko import START, START_DEVIATION, Game, Rated, expected, grown, updated
from climb.log import AttemptLog, SittingStore
from climb.ratings import RatingLog, standing_ratings
from climb.schema import Attempt, DifficultyRating, Sitting
from climb.sitting import lapsed
from climb.storage import Database


class Measured(BaseModel):
    model_config = ConfigDict(frozen=True)

    rating: float
    deviation: float
    games: int


class Played(BaseModel):
    """One ended cold sitting read as a game."""

    model_config = ConfigDict(frozen=True)

    day: date
    game: Game


def played(
    sittings: Iterable[Sitting],
    attempts: Iterable[Attempt],
    scores: Mapping[str, DifficultyRating],
    at: datetime,
) -> list[Played]:
    """The games of every cold sitting begun before `at` and ended by then. A
    problem with no score has no opponent, so its sitting is no game."""
    solved = {one.sitting_id for one in attempts if one.solved and one.finished_at <= at}
    games: list[Played] = []
    for one in sittings:
        if not one.cold or one.started_at >= at or one.problem_id not in scores:
            continue
        if (one.ended_at is None or one.ended_at > at) and lapsed(one, at) is None:
            continue
        stand = scores[one.problem_id]
        opponent = Rated(rating=stand.score, deviation=stand.deviation or 0.0)
        score = 1.0 if one.id in solved else 0.0
        games.append(
            Played(
                day=one.started_at.astimezone(UTC).date(), game=Game(opponent=opponent, score=score)
            )
        )
    return games


def replayed(games: Iterable[Played], at: datetime) -> Rated:
    """The rating at `at`: a period per UTC day, the deviation grown to `at`."""
    by_day: dict[date, list[Game]] = defaultdict(list)
    for one in games:
        by_day[one.day].append(one.game)
    player = Rated(rating=START, deviation=START_DEVIATION)
    last: date | None = None
    for day in sorted(by_day):
        if last is not None:
            player = grown(player, (day - last).days)
        player = updated(player, by_day[day])
        last = day
    if last is None:
        return player
    return grown(player, max((at.astimezone(UTC).date() - last).days, 0))


def measured(root: Database, user_id: str, at: datetime | None = None) -> Measured:
    at = at or datetime.now(UTC)
    games = _games(root, user_id, at)
    player = replayed(games, at)
    return Measured(rating=player.rating, deviation=player.deviation, games=len(games))


def chance(
    root: Database, user_id: str, problem_id: str, at: datetime | None = None
) -> float | None:
    """The chance the user solves the problem at `at`. None where the problem
    has no score to read the chance against."""
    at = at or datetime.now(UTC)
    stands = standing_ratings(RatingLog(root).ratings())
    if problem_id not in stands:
        return None
    player = replayed(_games(root, user_id, at, stands), at)
    stand = stands[problem_id]
    return expected(player, Rated(rating=stand.score, deviation=stand.deviation or 0.0))


def _games(
    root: Database,
    user_id: str,
    at: datetime,
    stands: Mapping[str, DifficultyRating] | None = None,
) -> list[Played]:
    # the scores as they stand now, not as they stood at the sitting
    scores = stands if stands is not None else standing_ratings(RatingLog(root).ratings())
    return played(SittingStore(root).all(user_id), AttemptLog(root).attempts(user_id), scores, at)
