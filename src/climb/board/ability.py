"""Each technique's ability on the contest scale, and the chance to solve read
from it: `api/mastery.md`."""

from collections import defaultdict
from collections.abc import Collection, Iterable, Mapping
from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict

from climb import glicko
from climb.attempt_claims import resolve_techniques
from climb.board.execution import score, sittings, through_first_solve
from climb.glicko import Game, Rated, expected
from climb.schema import Attempt, AttemptClaim, Problem, SelfLabel

# points a practice sitting is easier than a cold one; a starting guess the
# cold sittings' log-loss moves
GAP = 200.0


class Sat(BaseModel):
    """One sitting read as a game for each technique it counts for."""

    model_config = ConfigDict(frozen=True)

    day: date
    problem_id: str
    techniques: frozenset[str]
    score: float
    cold: bool


class Chance(BaseModel):
    model_config = ConfigDict(frozen=True)

    chance: float
    ability: float
    deviation: float
    games: int


def practised(
    attempts: Iterable[Attempt],
    problems: Mapping[str, Problem],
    claims: Mapping[str, AttemptClaim],
    labels: Mapping[str, SelfLabel],
    cold: Collection[str],
    at: datetime,
) -> list[Sat]:
    """The practice sittings as execution reads them, from the attempts ended
    by `at`. A cold sitting's attempts are left to the cold reading."""
    found: list[Sat] = []
    shown = [one for one in attempts if one.finished_at <= at and one.sitting_id not in cold]
    for whole in sittings(shown):
        problem = problems[whole[0].problem_id]
        if problem.defective:
            continue
        sitting = through_first_solve(whole)
        label = labels.get(sitting[-1].id)
        found.append(
            Sat(
                day=sitting[-1].finished_at.astimezone(UTC).date(),
                problem_id=problem.id,
                techniques=frozenset(
                    t for one in sitting for t in resolve_techniques(one, problem, claims)
                ),
                score=score(sitting, label.mode if label else None),
                cold=False,
            )
        )
    return found


def abilities(
    sat: Iterable[Sat],
    scores: Mapping[str, Rated],
    start: Rated,
    at: datetime,
    gap: float = GAP,
) -> dict[str, tuple[Rated, int]]:
    """Each technique's ability at `at` and the games it read. A sitting on a
    problem with no score has no opponent, and counts for no ability."""
    games: dict[str, list[tuple[date, Game]]] = defaultdict(list)
    for one in sat:
        if one.problem_id not in scores:
            continue
        rated = scores[one.problem_id]
        easier = Rated(rating=rated.rating - gap, deviation=rated.deviation)
        opponent = rated if one.cold else easier
        for technique in one.techniques:
            games[technique].append((one.day, Game(opponent=opponent, score=one.score)))
    return {
        technique: (glicko.replayed(found, at, start), len(found))
        for technique, found in games.items()
    }


def chance(
    held: Mapping[str, tuple[Rated, int]], start: Rated, technique: str, score: Rated
) -> Chance:
    """A technique no sitting reached is at the start."""
    ability, games = held.get(technique, (start, 0))
    return Chance(
        chance=expected(ability, score),
        ability=ability.rating,
        deviation=ability.deviation,
        games=games,
    )


def weakest(
    held: Mapping[str, tuple[Rated, int]], start: Rated, techniques: Iterable[str], score: Rated
) -> Chance | None:
    """A problem's chance: its weakest technique's. None on a problem with no
    technique."""
    found = [chance(held, start, technique, score) for technique in techniques]
    return min(found, key=lambda one: one.chance, default=None)
