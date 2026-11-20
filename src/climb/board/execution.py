"""Each technique's execution reading, folded from its sittings:
`api/mastery.md`."""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence

from climb.attempt_claims import resolve_techniques
from climb.ids import settings_hash
from climb.schema import Attempt, AttemptClaim, FailureMode, Problem, SelfLabel

# the starting values `api/mastery.md` gives, each moved only on what the log
# measures
FIRST_SOLVE = 1.0
LATER_SOLVE = 0.5
SYNTAX_FAILURE = 0.25
EVIDENCE = 3  # sittings before the board shows a number rather than unknown
MISSED = {FailureMode.GAP, FailureMode.RUST}
SETTINGS_HASH = settings_hash([FIRST_SOLVE, LATER_SOLVE, SYNTAX_FAILURE, EVIDENCE, sorted(MISSED)])


def score(attempts: Sequence[Attempt], label: FailureMode | None) -> float:
    """One sitting, over its attempts in the order they were submitted."""
    if label in MISSED:
        return 0.0
    if attempts[0].solved_unaided:
        return FIRST_SOLVE
    if any(one.solved_unaided for one in attempts):
        return LATER_SOLVE
    return SYNTAX_FAILURE if label is FailureMode.SYNTAX else 0.0


def sittings(attempts: Iterable[Attempt]) -> list[list[Attempt]]:
    """Attempts grouped by sitting, each in submission order. An attempt no
    sitting of the engine's minted is a sitting of its own."""
    grouped: dict[str, list[Attempt]] = defaultdict(list)
    for one in attempts:
        grouped[one.sitting_id or f"attempt:{one.id}"].append(one)
    return [sorted(group, key=lambda one: one.finished_at) for group in grouped.values()]


def through_first_solve(sitting: Sequence[Attempt]) -> Sequence[Attempt]:
    """The attempts a sitting's verdict reads: `flows/drill-loop.md`."""
    solve = next((n for n, one in enumerate(sitting) if one.solved_unaided), None)
    return sitting if solve is None else sitting[: solve + 1]


def execution(
    attempts: Iterable[Attempt],
    problems: Mapping[str, Problem],
    claims: Mapping[str, AttemptClaim],
    labels: Mapping[str, SelfLabel],
) -> dict[str, tuple[int, float | None]]:
    """Each technique's sittings counted, and its reading where enough of them
    stand. A sitting counts for every technique its attempts resolve to."""
    scores: dict[str, list[float]] = defaultdict(list)
    for whole in sittings(attempts):
        problem = problems[whole[0].problem_id]
        if problem.defective:
            continue
        sitting = through_first_solve(whole)
        label = labels.get(sitting[-1].id)
        value = score(sitting, label.mode if label else None)
        techniques = {t for one in sitting for t in resolve_techniques(one, problem, claims)}
        for technique in techniques:
            scores[technique].append(value)
    return {
        technique: (len(found), sum(found) / len(found) if len(found) >= EVIDENCE else None)
        for technique, found in scores.items()
    }
