import pytest
from helpers import PROVENANCE_FIELDS, T0, make_problem
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from climb.problems import ProblemStore
from climb.schema import CaseOutcome, Trial
from climb.trials import TrialLog


def trial(outcome=CaseOutcome.PASSED, passed=5, run=5, **overrides) -> Trial:
    fields = {
        "id": "t1",
        "created_at": T0,
        "problem_id": "p1",
        "try_number": 1,
        "outcome": outcome,
        "cases_passed": passed,
        "cases_run": run,
        "cap_ms": 2000,
        "runner": "subprocess",
        **PROVENANCE_FIELDS,
    } | overrides
    return Trial.model_validate(fields)


def test_a_trial_that_passed_every_case_solved():
    assert trial().solved
    assert not trial(CaseOutcome.WRONG, passed=4).solved


@pytest.mark.parametrize(
    ("outcome", "passed", "run"),
    [
        (CaseOutcome.PASSED, 4, 5),
        (CaseOutcome.WRONG, 5, 5),
        (CaseOutcome.WRONG, 6, 5),
        (None, 0, 5),
        (CaseOutcome.CRASHED, 0, 0),
    ],
)
def test_the_counts_agree_with_the_outcome(outcome, passed, run):
    """A pass is every case passed, and an outcome needs a case that ran."""
    with pytest.raises(ValidationError):
        trial(outcome, passed, run)


def test_code_that_ran_no_case_has_no_outcome():
    assert not trial(None, 0, 0).solved


def test_a_trial_carries_the_members_configuration():
    with pytest.raises(ValidationError):
        trial(call_id=None)


def test_a_stored_trial_reads_back_and_is_never_rewritten(database):
    """Product data, append-only, as the data classes of `database/README.md`
    give."""
    ProblemStore(database).put(make_problem())
    TrialLog(database).append(trial())

    assert TrialLog(database).for_problem("p1") == [trial()]
    with pytest.raises(DBAPIError), database.begin() as conn:
        conn.execute(text("UPDATE trials SET cases_passed = 0"))
