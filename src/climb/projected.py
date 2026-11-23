"""A user's projected contest rating, from each technique's chance to solve
over a representative contest: `api/projection.md`."""

import json
import random
import statistics
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
from functools import cache
from importlib import resources

from pydantic import BaseModel, ConfigDict

from climb.glicko import Rated
from climb.measured import technique_abilities
from climb.storage import Database

DRAWS = 400
# fixed, so one log reads one deviation on every read
SEED = 0
LOW, HIGH = -1000.0, 6000.0


class ContestProblem(BaseModel):
    """Problems of one rating meeting the same needs. A need is met by any one
    of its techniques."""

    model_config = ConfigDict(frozen=True)

    rating: float
    needs: tuple[tuple[str, ...], ...]
    count: int


class Projected(BaseModel):
    model_config = ConfigDict(frozen=True)

    rating: float
    deviation: float
    # the contest's techniques a sitting reached
    techniques: int


@cache
def contest() -> tuple[ContestProblem, ...]:
    raw = json.loads(resources.files("climb").joinpath("contest.json").read_text())
    return tuple(ContestProblem.model_validate(one) for one in raw["problems"])


def projected(root: Database, user_id: str, at: datetime | None = None) -> Projected:
    held, start = technique_abilities(root, user_id, at)
    return project({key: rated for key, (rated, _) in held.items()}, start, contest())


def project(
    held: Mapping[str, Rated], start: Rated, problems: Sequence[ContestProblem]
) -> Projected:
    """The rating at the mean abilities, and its spread over draws of them."""
    names = sorted({t for one in problems for need in one.needs for t in need})
    rating = _performance(_held(held, start.rating, names, None), start.rating, problems)
    draw = random.Random(SEED)
    spread: list[float] = []
    for _ in range(DRAWS):
        # every technique no sitting reached is the start, so shares its draw
        begun = draw.gauss(start.rating, start.deviation)
        spread.append(_performance(_held(held, begun, names, draw), begun, problems))
    reached = len(held.keys() & set(names))
    return Projected(rating=rating, deviation=statistics.pstdev(spread), techniques=reached)


def _held(
    held: Mapping[str, Rated], start: float, names: Sequence[str], draw: random.Random | None
) -> dict[str, float]:
    found = {t: start for t in names}
    for t, one in held.items():
        found[t] = draw.gauss(one.rating, one.deviation) if draw else one.rating
    return found


def _performance(
    ability: Mapping[str, float], start: float, problems: Sequence[ContestProblem]
) -> float:
    """The rating whose expected solves on the contest equal the user's."""
    solves = sum(one.count * _solve(_weakest(ability, start, one), one.rating) for one in problems)
    ratings = Counter[float]()
    for one in problems:
        ratings[one.rating] += one.count
    low, high = LOW, HIGH
    for _ in range(40):
        mid = (low + high) / 2
        if sum(count * _solve(mid, r) for r, count in ratings.items()) < solves:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _weakest(ability: Mapping[str, float], start: float, problem: ContestProblem) -> float:
    # a problem with no technique the engine names reads the start
    if not problem.needs:
        return start
    return min(max(ability[t] for t in need) for need in problem.needs)


def _solve(ability: float, rating: float) -> float:
    return 1 / (1 + 10 ** ((rating - ability) / 400))
