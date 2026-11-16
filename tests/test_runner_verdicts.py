from helpers import PROVENANCE

from climb.mint import case
from climb.runner.execution import CaseRun, RunOutcome
from climb.runner.verdicts import result
from climb.schema import RETURNED_KEPT, CaseOutcome

EXPECTS_TWO = case("p1", [1], 2, provenance=PROVENANCE)


def test_a_wrong_case_keeps_what_it_returned():
    """A reopened sitting shows the failing case's return without a rerun."""
    ran = CaseRun(RunOutcome.RETURNED, value={"b": None, "a": 3}, elapsed_ms=1)

    kept = result(EXPECTS_TWO, ran)

    assert (kept.outcome, kept.returned) == (CaseOutcome.WRONG, '{"a": 3, "b": null}')


def test_a_passing_case_keeps_no_return():
    passed = result(EXPECTS_TWO, CaseRun(RunOutcome.RETURNED, value=2, elapsed_ms=1))

    assert passed.returned is None


def test_a_return_past_the_bound_is_not_kept():
    """The log would otherwise grow by a case's weight per wrong submission."""
    big = "x" * RETURNED_KEPT

    wrong = result(EXPECTS_TWO, CaseRun(RunOutcome.RETURNED, value=big, elapsed_ms=1))

    assert (wrong.outcome, wrong.returned) == (CaseOutcome.WRONG, None)
