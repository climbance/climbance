from helpers import PROVENANCE_FIELDS, make_problem

from climb.diagnosing import slip_mutants
from climb.diagnosing.slips import outside, slips
from climb.schema import ExpectedSource, FailureMode, Template, TestCase

FORM = """def solve(xs):
    best = xs[0]
    for x in xs:
        best = max(best, x)
    return best
"""

# the form renamed, behind a guard the problem adds
CANONICAL = """def solve(readings: list[int]) -> int:
    if not readings:
        return -1
    top = readings[0]
    for r in readings:
        top = max(top, r)
    return top
"""

TEMPLATE = Template(id="t1", slug="largest", title="largest", trigger="the largest", code=FORM)


def case(id: str, args: list, expected, round: int | None = 0) -> TestCase:
    return TestCase(
        id=id,
        problem_id="p1",
        args=args,
        expected=expected,
        expected_from=ExpectedSource.REFERENCE,
        round=round,
        **PROVENANCE_FIELDS,
    )


CASES = [case("c1", [[3, 9, 2]], 9), case("c2", [[]], -1)]


def problem(id: str = "p1"):
    return make_problem(id, target_technique=None, target_template_id="t1")


def test_a_renamed_form_line_is_inside_and_an_added_guard_outside():
    """A canonical names the form's variables after its problem."""
    assert outside(FORM, CANONICAL) == {2, 3}


def test_a_form_line_the_canonical_rewrote_gives_no_split():
    """A rewritten form line would sit among the outside lines, and a slip
    planted there would be a form fault."""
    rewritten = CANONICAL.replace("top = max(top, r)", "top = r if r > top else top")

    assert outside(FORM, rewritten) is None
    assert slips(problem(), TEMPLATE, rewritten, CASES) == []


def test_a_slip_mutant_changes_a_line_outside_the_form_and_fails_a_case():
    found = slips(problem(), TEMPLATE, CANONICAL, CASES)

    assert found
    assert {one.mode for one in found} == {FailureMode.SYNTAX}
    assert {one.line for one in found} <= {2, 3}
    assert {one.problem_id for one in found} == {"p1"}
    assert all(one.code != CANONICAL for one in found)


def test_a_mutant_no_case_fails_is_dropped():
    """Without the empty list, no case sees the guard's return value move."""
    every = slips(problem(), TEMPLATE, CANONICAL, CASES)
    fewer = slips(problem(), TEMPLATE, CANONICAL, CASES[:1])

    assert {one.change for one in fewer} < {one.change for one in every}
    assert all(one.case_args == CASES[0].args for one in fewer)


def test_the_separating_case_is_not_run():
    """A slip is no slowdown, and that case is the one sized to time out."""
    separating = case("c3", [[]], -1, None)

    assert slips(problem(), TEMPLATE, CANONICAL, [CASES[0], separating]) == slips(
        problem(), TEMPLATE, CANONICAL, CASES[:1]
    )


def test_a_problem_written_for_a_technique_gives_no_slip():
    """It names no form, so no line of its canonical is outside one."""
    technique = make_problem("p1")

    assert slip_mutants([technique], {"t1": TEMPLATE}, {"p1": CANONICAL}, {"p1": CASES}) == []


def test_one_change_to_one_line_shape_counts_once():
    """Two canonicals sharing a decoder would weigh one mistake twice."""
    once = slip_mutants([problem("p1")], {"t1": TEMPLATE}, {"p1": CANONICAL}, {"p1": CASES})
    twice = slip_mutants(
        [problem("p1"), problem("p2")],
        {"t1": TEMPLATE},
        {"p1": CANONICAL, "p2": CANONICAL},
        {"p1": CASES, "p2": CASES},
    )

    assert len(twice) == len(once)
