"""The difficulty fit's arithmetic: `cli/difficulty/fits.md`."""

import math
from collections import defaultdict
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

# a weak normal prior on every parameter, in logits: it keeps a problem every
# member solved, or none did, at a finite difficulty with a wide deviation
PRIOR_SD = 3.0
ROUNDS = 200
TOLERANCE = 1e-6


@dataclass(frozen=True)
class Outcome[M: Hashable, P: Hashable]:
    member: M
    problem: P
    solved: bool


@dataclass(frozen=True)
class Fitted[M: Hashable, P: Hashable]:
    ability: dict[M, float]
    difficulty: dict[P, float]
    deviation: dict[P, float]  # one standard error, in logits


@dataclass(frozen=True)
class Link:
    slope: float
    intercept: float

    def score(self, difficulty: float) -> float:
        return self.slope * difficulty + self.intercept

    def difficulty(self, score: float) -> float:
        return (score - self.intercept) / self.slope


def chance(ability: float, difficulty: float) -> float:
    return 1 / (1 + math.exp(difficulty - ability))


def fit[M: Hashable, P: Hashable](outcomes: Sequence[Outcome[M, P]]) -> Fitted[M, P]:
    """Abilities and difficulties at the posterior's mode, by one Newton step
    per parameter per round."""
    by_member: dict[M, list[Outcome[M, P]]] = defaultdict(list)
    by_problem: dict[P, list[Outcome[M, P]]] = defaultdict(list)
    for one in outcomes:
        by_member[one.member].append(one)
        by_problem[one.problem].append(one)
    ability = dict.fromkeys(by_member, 0.0)
    difficulty = dict.fromkeys(by_problem, 0.0)
    precision = 1 / PRIOR_SD**2
    for _ in range(ROUNDS):
        moved = 0.0
        for member, mine in by_member.items():
            p = [chance(ability[member], difficulty[o.problem]) for o in mine]
            grad = (
                sum(o.solved - q for o, q in zip(mine, p, strict=True))
                - precision * ability[member]
            )
            step = grad / (sum(q * (1 - q) for q in p) + precision)
            ability[member] += step
            moved = max(moved, abs(step))
        for problem, theirs in by_problem.items():
            p = [chance(ability[o.member], difficulty[problem]) for o in theirs]
            grad = (
                sum(q - o.solved for o, q in zip(theirs, p, strict=True))
                - precision * difficulty[problem]
            )
            step = grad / (sum(q * (1 - q) for q in p) + precision)
            difficulty[problem] += step
            moved = max(moved, abs(step))
        if moved < TOLERANCE:
            break
    deviation = {
        problem: (
            sum(
                chance(ability[o.member], difficulty[problem])
                * (1 - chance(ability[o.member], difficulty[problem]))
                for o in theirs
            )
            + precision
        )
        ** -0.5
        for problem, theirs in by_problem.items()
    }
    return Fitted(ability, difficulty, deviation)


def link(pairs: Sequence[tuple[float, float]]) -> Link:
    """The least-squares line from a fitted difficulty to a contest rating."""
    if len(pairs) < 2:
        raise ValueError("a line needs two anchors")
    xs, ys = [x for x, _ in pairs], [y for _, y in pairs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    spread = sum((x - mx) ** 2 for x in xs)
    if spread == 0:
        raise ValueError("the anchors fitted at one difficulty, so no line is set")
    slope = sum((x - mx) * (y - my) for x, y in pairs) / spread
    return Link(slope, my - slope * mx)


def log_loss(predicted: Sequence[tuple[float, bool]]) -> float:
    eps = 1e-12
    return -sum(
        math.log(max(p, eps) if solved else max(1 - p, eps)) for p, solved in predicted
    ) / len(predicted)
