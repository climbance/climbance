from helpers import T0, make_problem

from climb.diagnoser import Tool
from climb.diagnosing import Tasks
from climb.judging.labelled import LabelledMutant
from climb.mutation import Operator
from climb.schema import (
    Attempt,
    AttemptVerification,
    CaseOutcome,
    CaseResult,
    FailureMode,
    Template,
    TestCase,
)

TEMPLATE = Template(id="t1", slug="largest", title="largest", trigger="the largest", code="x")
PROBLEM = make_problem("p1")
ATTEMPT = Attempt(
    id="a1", user_id="u-4f9c2a", problem_id="p1", finished_at=T0, solved=False, code="pass"
)


def case(id: str, args: list, expected) -> TestCase:
    return TestCase.model_validate(
        {
            "id": id,
            "problem_id": "p1",
            "args": args,
            "expected": expected,
            "expected_from": "reference",
            "round": 0,
            "model": "a-model",
            "effort": "medium",
            "pin": "",
            "prompt_hash": "0123456789ab",
            "call_id": "call-1",
        }
    )


RUN = AttemptVerification(
    id="v1",
    created_at=T0,
    attempt_id="a1",
    cap_ms=2000,
    runner="local",
    results=[
        CaseResult(case_id="c1", outcome=CaseOutcome.PASSED, elapsed_ms=1),
        CaseResult(case_id="c2", outcome=CaseOutcome.WRONG, elapsed_ms=1, returned="7"),
        CaseResult(case_id="c3", outcome=CaseOutcome.CRASHED, error="IndexError"),
    ],
)
CASES = {
    one.id: one for one in (case("c1", [[1]], 1), case("c2", [[3, 9]], 9), case("c3", [[]], 0))
}


def tasks(*tools: Tool) -> Tasks:
    return Tasks(
        problems={"p1": PROBLEM},
        templates={"t1": TEMPLATE},
        tools=frozenset(tools),
        cases=CASES,
        runs={"a1": RUN},
    )


def test_the_divergence_tool_shows_the_first_case_the_attempt_failed():
    """The first failure, not the last: later cases may fail for the same
    cause and add nothing."""
    failed = tasks(Tool.DIVERGENCE).attempt(ATTEMPT).failed

    assert failed == "arguments: [[3, 9]]\nexpected: 9\nreturned: 7"


def test_the_baseline_shows_no_case():
    """A case already in the baseline would leave the tool nothing to add."""
    assert tasks().attempt(ATTEMPT).failed is None


def test_a_crash_shows_what_it_raised():
    run = RUN.model_copy(update={"results": RUN.results[2:]})
    found = Tasks(
        problems={"p1": PROBLEM},
        templates={},
        tools=frozenset({Tool.DIVERGENCE}),
        cases=CASES,
        runs={"a1": run},
    )

    assert found.attempt(ATTEMPT).failed == "arguments: [[]]\nexpected: 0\nraised: IndexError"


def test_a_mutant_shows_the_case_it_fails_under_the_tool():
    one = LabelledMutant(
        template_id="t1",
        form_digest="d1",
        code="return 1\n",
        line=1,
        change="< → <=",
        operator=Operator.BOUNDARY,
        mode=FailureMode.RUST,
        case_args=[[2, 5]],
        case_expected=5,
        outcome=CaseOutcome.WRONG,
        returned=2,
    )

    assert tasks().mutant(one).failed is None
    assert (
        tasks(Tool.DIVERGENCE).mutant(one).failed == "arguments: [[2, 5]]\nexpected: 5\nreturned: 2"
    )
