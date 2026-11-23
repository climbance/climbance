"""Glicko-1 on the contest scale, from Glickman, *The Glicko system* (1995).
`api/rating.md` gives the periods, the start and why the deviations combine."""

import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict

Q = math.log(10) / 400
START = 1500.0
START_DEVIATION = 350.0
# lets a deviation of 50 widen back to 350 over a year of daily periods
GROWTH = math.sqrt((START_DEVIATION**2 - 50**2) / 365)


class Rated(BaseModel):
    model_config = ConfigDict(frozen=True)

    rating: float
    deviation: float


class Game(BaseModel):
    model_config = ConfigDict(frozen=True)

    opponent: Rated
    score: float  # 1 solved, 0 not


def _g(deviation: float) -> float:
    return 1 / math.sqrt(1 + 3 * Q**2 * deviation**2 / math.pi**2)


def expected(player: Rated, opponent: Rated) -> float:
    """The chance the player beats the opponent, both deviations combined."""
    spread = math.hypot(player.deviation, opponent.deviation)
    return 1 / (1 + 10 ** (-_g(spread) * (player.rating - opponent.rating) / 400))


def grown(player: Rated, periods: int) -> Rated:
    """The deviation widened over `periods`, capped at the start's."""
    widened = math.sqrt(player.deviation**2 + GROWTH**2 * periods)
    return Rated(rating=player.rating, deviation=min(widened, START_DEVIATION))


def updated(player: Rated, games: Sequence[Game]) -> Rated:
    """One period's games, each read against the period's starting rating."""
    if not games:
        return player
    terms = [
        (_g(one.opponent.deviation), _one_sided(player, one.opponent), one.score) for one in games
    ]
    inverse_d2 = Q**2 * sum(g**2 * e * (1 - e) for g, e, _ in terms)
    precision = 1 / player.deviation**2 + inverse_d2
    rating = player.rating + Q / precision * sum(g * (s - e) for g, e, s in terms)
    return Rated(rating=rating, deviation=math.sqrt(1 / precision))


def _one_sided(player: Rated, opponent: Rated) -> float:
    # the update reads the opponent's deviation alone, as Glickman's step 2 does
    return 1 / (1 + 10 ** (-_g(opponent.deviation) * (player.rating - opponent.rating) / 400))


def replayed(
    games: Iterable[tuple[date, Game]],
    at: datetime,
    start: Rated | None = None,
) -> Rated:
    """The rating at `at`: a period per UTC day, the deviation grown to `at`."""
    by_day: dict[date, list[Game]] = defaultdict(list)
    for day, game in games:
        by_day[day].append(game)
    player = start or Rated(rating=START, deviation=START_DEVIATION)
    last: date | None = None
    for day in sorted(by_day):
        if last is not None:
            player = grown(player, (day - last).days)
        player = updated(player, by_day[day])
        last = day
    if last is None:
        return player
    return grown(player, max((at.astimezone(UTC).date() - last).days, 0))
