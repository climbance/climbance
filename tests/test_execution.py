from datetime import UTC, datetime, timedelta

from helpers import make_problem

from climb.board.execution import execution, score
from climb.schema import Attempt, FailureMode, ProblemStatus, RetirementReason, SelfLabel

T0 = datetime(2026, 9, 1, 10, tzinfo=UTC)
MINUTE = timedelta(minutes=1)
PROBLEMS = {
    "p1": make_problem("p1", techniques=["greedy"]),
    "bad": make_problem(
        "bad",
        techniques=["greedy"],
        status=ProblemStatus.RETIRED,
        retired_reason=RetirementReason.DEFECTIVE,
    ),
}


def submitted(sitting: str, n: int, *, solved: bool, problem: str = "p1") -> Attempt:
    return Attempt(
        id=f"{sitting}-{n}",
        user_id="u-4f9c2a",
        problem_id=problem,
        sitting_id=sitting,
        finished_at=T0 + n * MINUTE,
        solved=solved,
    )


def labelled(attempt: Attempt, mode: FailureMode) -> SelfLabel:
    return SelfLabel(
        id=f"l-{attempt.id}", attempt_id=attempt.id, created_at=attempt.finished_at, mode=mode
    )


def test_a_first_submission_solve_counts_more_than_a_later_one():
    """A failed submission showed a case, so the solve after it counts half."""
    first = [submitted("s", 0, solved=True)]
    later = [submitted("s", 0, solved=False), submitted("s", 1, solved=True)]
    assert (score(first, None), score(later, None)) == (1.0, 0.5)


def test_the_last_attempt_s_label_adjusts_the_sitting():
    """`syntax` counts less as a failure, and `gap` or `rust` count as one."""
    failed = [submitted("s", 0, solved=False)]
    solved = [submitted("s", 0, solved=True)]
    assert score(failed, FailureMode.SYNTAX) == 0.25
    assert score(solved, FailureMode.GAP) == 0.0
    assert score(failed, None) == 0.0


def test_a_reading_waits_for_three_sittings():
    """Two sittings count but show no number, and the third gives the mean."""
    two = [submitted("a", 0, solved=True), submitted("b", 0, solved=False)]
    assert execution(two, PROBLEMS, {}, {})["greedy"] == (2, None)
    three = [*two, submitted("c", 0, solved=False), submitted("c", 1, solved=True)]
    assert execution(three, PROBLEMS, {}, {})["greedy"] == (3, 0.5)


def test_a_sitting_counts_once_however_many_attempts_it_holds():
    """Counting attempts would punish a user who submits often."""
    many = [submitted("a", n, solved=n == 3) for n in range(4)]
    assert execution(many, PROBLEMS, {}, {})["greedy"][0] == 1


def test_a_defective_problem_s_sittings_count_for_nothing():
    """Its verdict decides something other than the form."""
    assert execution([submitted("a", 0, solved=True, problem="bad")], PROBLEMS, {}, {}) == {}


def test_the_label_is_read_from_the_sitting_s_last_attempt():
    """A `gap` on the last attempt zeroes a solve the first attempt made."""
    sitting = [submitted("a", 0, solved=True), submitted("a", 1, solved=True)]
    labels = {sitting[1].id: labelled(sitting[1], FailureMode.GAP)}
    found = execution(
        [*sitting, *(submitted(s, 0, solved=True) for s in "bc")], PROBLEMS, {}, labels
    )
    assert found["greedy"] == (3, 2 / 3)
