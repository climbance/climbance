"""A user's measured rating, replayed from the user's cold sittings on every
read. `api/rating.md` gives the games, the periods and the scores read."""

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict

from climb import glicko
from climb.attempt_claims import standing_attempt_claims
from climb.board.ability import GAP, Chance, Sat, abilities, practised, weakest
from climb.glicko import START, START_DEVIATION, Game, Rated, expected
from climb.log import AttemptLog, SittingStore, latest_by_attempt
from climb.ratings import RatingLog, standing_ratings
from climb.schema import Attempt, AttemptClaim, DifficultyRating, Problem, SelfLabel, Sitting
from climb.sitting import lapsed
from climb.solution_claims import load_problems
from climb.storage import Database
from climb.techniques import with_ancestors

# the candidate gaps, in points on the contest scale
GAPS = tuple(float(points) for points in range(0, 501, 50))
# a chance of exactly 0 or 1 would make one miss an infinite loss
FLOOR = 1e-6


class Measured(BaseModel):
    model_config = ConfigDict(frozen=True)

    rating: float
    deviation: float
    games: int


class Played(BaseModel):
    """One ended cold sitting read as a game."""

    model_config = ConfigDict(frozen=True)

    day: date
    problem_id: str
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
                day=one.started_at.astimezone(UTC).date(),
                problem_id=one.problem_id,
                game=Game(opponent=opponent, score=score),
            )
        )
    return games


def replayed(games: Iterable[Played], at: datetime) -> Rated:
    return glicko.replayed(((one.day, one.game) for one in games), at)


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


def technique_chance(
    root: Database,
    user_id: str,
    techniques: Iterable[str],
    score: float,
    deviation: float = 0.0,
    at: datetime | None = None,
) -> Chance | None:
    """The chance the user solves a problem of `score` needing `techniques`
    under cold conditions, its weakest technique's: `api/mastery.md`."""
    at = at or datetime.now(UTC)
    stands = standing_ratings(RatingLog(root).ratings())
    problems = {one.id: one for one in load_problems(root)}
    read = _read(root, user_id, stands, problems)
    return _chance(read, techniques, Rated(rating=score, deviation=deviation), at, GAP)


@dataclass(frozen=True)
class _Read:
    stands: Mapping[str, DifficultyRating]
    problems: Mapping[str, Problem]
    attempts: list[Attempt]
    sittings: list[Sitting]
    claims: Mapping[str, AttemptClaim]
    labels: Mapping[str, SelfLabel]


def _read(
    root: Database,
    user_id: str,
    stands: Mapping[str, DifficultyRating],
    problems: Mapping[str, Problem],
) -> _Read:
    log = AttemptLog(root)
    return _Read(
        stands=stands,
        problems=problems,
        attempts=log.attempts(user_id),
        sittings=SittingStore(root).all(user_id),
        claims=standing_attempt_claims(log.claims(user_id)),
        labels=latest_by_attempt(log.self_labels(user_id)),
    )


def _chance(
    read: _Read, techniques: Iterable[str], score: Rated, at: datetime, gap: float
) -> Chance | None:
    held, start = _abilities(read, at, gap)
    return weakest(held, start, techniques, score)


def technique_abilities(
    root: Database, user_id: str, at: datetime | None = None
) -> tuple[dict[str, tuple[Rated, int]], Rated]:
    """Each technique's ability and games under cold conditions, and the start
    a technique no sitting reached is held at."""
    at = at or datetime.now(UTC)
    stands = standing_ratings(RatingLog(root).ratings())
    problems = {one.id: one for one in load_problems(root)}
    return _abilities(_read(root, user_id, stands, problems), at, GAP)


def _abilities(read: _Read, at: datetime, gap: float) -> tuple[dict[str, tuple[Rated, int]], Rated]:
    cold = played(read.sittings, read.attempts, read.stands, at)
    general = replayed(cold, at)
    # a wide deviation, so the technique's own sittings soon outweigh the start
    start = Rated(rating=general.rating if cold else START, deviation=START_DEVIATION)
    sat = [
        Sat(
            day=one.day,
            problem_id=one.problem_id,
            techniques=frozenset(with_ancestors(read.problems[one.problem_id].techniques)),
            score=one.game.score,
            cold=True,
        )
        for one in cold
        if not read.problems[one.problem_id].defective
    ]
    sat += practised(
        read.attempts,
        read.problems,
        read.claims,
        read.labels,
        {one.id for one in read.sittings if one.cold},
        at,
    )
    scores = {
        key: Rated(rating=one.score, deviation=one.deviation or 0.0)
        for key, one in read.stands.items()
    }
    return abilities(sat, scores, start, at, gap), start


class ChanceLoss(BaseModel):
    """The chance's log-loss over the cold sittings, each held out of the gap's
    fit, and the gap fitted on them all."""

    model_config = ConfigDict(frozen=True)

    sittings: int
    users: int
    log_loss: float | None
    gap: float


def chance_loss(
    root: Database, gaps: Sequence[float] = GAPS, at: datetime | None = None
) -> ChanceLoss:
    """Each cold sitting's chance replayed from the log before it began, at
    every candidate gap: `api/mastery.md`."""
    at = at or datetime.now(UTC)
    stands = standing_ratings(RatingLog(root).ratings())
    problems = {one.id: one for one in load_problems(root)}
    rows: list[list[float]] = []
    users: set[str] = set()
    for user_id in sorted({one.user_id for one in SittingStore(root).all() if one.cold}):
        read = _read(root, user_id, stands, problems)
        for one in read.sittings:
            game = played([one], read.attempts, stands, at)
            if not game or problems[one.problem_id].defective:
                continue
            stand = stands[one.problem_id]
            score = Rated(rating=stand.score, deviation=stand.deviation or 0.0)
            techniques = problems[one.problem_id].techniques
            found = [_chance(read, techniques, score, one.started_at, gap) for gap in gaps]
            if found[0] is None:
                continue
            rows.append([loss(c.chance, game[0].game.score) for c in found if c is not None])
            users.add(user_id)
    log_loss, gap = held_out(rows, gaps)
    return ChanceLoss(sittings=len(rows), users=len(users), log_loss=log_loss, gap=gap)


def loss(chance: float, outcome: float) -> float:
    chance = min(max(chance, FLOOR), 1 - FLOOR)
    return -math.log(chance if outcome else 1 - chance)


def held_out(rows: Sequence[Sequence[float]], gaps: Sequence[float]) -> tuple[float | None, float]:
    """The mean loss of each row at the gap fitted on the other rows, and the
    gap fitted on every row. A fit on no row keeps the starting gap."""
    totals = [sum(row[k] for row in rows) for k in range(len(gaps))]

    def fitted(without: Sequence[float] | None) -> int:
        def key(k: int) -> tuple[float, float]:
            total = totals[k] - (without[k] if without is not None else 0.0)
            return (round(total, 9), abs(gaps[k] - GAP))

        return min(range(len(gaps)), key=key)

    gap = gaps[fitted(None)]
    if not rows:
        return None, gap
    return sum(row[fitted(row)] for row in rows) / len(rows), gap
