from datetime import UTC, datetime

from test_key_lines import in_range

from climb.judging import items, key_lines, labelled_mutants
from climb.mutation import Operator
from climb.schema import FailureMode, ItemStatus, Template, TemplateCase

NOW = datetime(2026, 11, 17, tzinfo=UTC)

FORM = """def solve(xs, target):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
"""


def template() -> Template:
    return Template.model_validate(
        {
            "id": "t-1",
            "slug": "binary-search",
            "title": "binary search",
            "trigger": "a sorted list and one value to find",
            "code": FORM,
            "cases": [
                TemplateCase(args=[[1, 3, 5, 7], 7], expected=3),
                TemplateCase(args=[[1, 3, 5, 7], 1], expected=0),
                TemplateCase(args=[[1, 3, 5, 7], 4], expected=-1),
                TemplateCase(args=[[], 4], expected=-1),
            ],
        }
    )


def test_every_flawed_item_and_wrong_choice_is_labelled_rust():
    """A one-change mutant of a form is the form coming back in pieces."""
    judged, keyed = items(template(), now=NOW), key_lines(template(), now=NOW)
    found = labelled_mutants(judged, keyed)

    assert found
    assert {one.mode for one in found} == {FailureMode.RUST}
    assert all(one.operator in Operator for one in found)


def test_a_wrong_choice_carries_the_form_with_its_line_swapped():
    """The diagnosis call reads whole code, so a choice is spliced back into
    the form it was blanked from."""
    keyed = key_lines(template(), now=NOW)
    found = labelled_mutants([], keyed)
    item = keyed[0]
    wrong = [one for one in item.choices if not one.correct]

    mine = [one for one in found if one.line == item.line]
    assert {one.change for one in mine} == {one.change for one in wrong}
    form = item.code.splitlines()
    indent = form[item.line - 1][: -len(form[item.line - 1].lstrip())]
    for one in mine:
        lines = one.code.splitlines()
        assert lines[item.line - 1] in {indent + choice.text for choice in wrong}
        assert (
            lines[: item.line - 1] + lines[item.line :] == form[: item.line - 1] + form[item.line :]
        )


def test_a_mutant_both_exercises_serve_counts_once():
    """Counting it twice would weigh a mistake by how many exercises show it."""
    judged, keyed = items(template(), now=NOW), key_lines(template(), now=NOW)
    both = labelled_mutants(judged, keyed)
    apart = labelled_mutants(judged, []), labelled_mutants([], keyed)

    assert len({one.code for one in both}) == len(both)
    assert len(both) < len(apart[0]) + len(apart[1])


def test_a_retired_item_and_a_clean_one_yield_nothing():
    """A clean item has no mistake, and a retired one shows a form the
    template no longer holds."""
    judged = items(template(), now=NOW)
    retired = [one.model_copy(update={"status": ItemStatus.RETIRED}) for one in judged]

    assert labelled_mutants([one for one in judged if one.clean], []) == []
    assert labelled_mutants(retired, []) == []


def test_a_two_line_choice_is_spliced_over_both_lines_of_its_blank():
    """A statement's choice replaces the whole statement, so the mutant differs
    from the form on the one line its change moved."""
    keyed = [one for one in key_lines(in_range(), now=NOW) if one.line == 4]
    form = keyed[0].code.splitlines()

    for one in labelled_mutants([], keyed):
        lines = one.code.splitlines()
        assert len(lines) == len(form)
        assert sum(a != b for a, b in zip(lines, form, strict=True)) == 1
