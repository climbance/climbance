from datetime import UTC, datetime

import pytest
from matching import card as card_record
from matching import seeded
from matching import template as template_record
from test_judging import card, template

from climb.judging import build_key_lines, key_lines
from climb.judging.build import WIDTH
from climb.keylines import KeyLineStore
from climb.schema import CaseOutcome, ItemStatus, KeyLineChoice, KeyLineItem, TemplateCase

NOW = datetime(2026, 11, 16, tzinfo=UTC)

FORM = """def solve(xs, target):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return lo
"""

CASES = [
    TemplateCase(args=[[1, 3, 5, 7], 5], expected=2),
    TemplateCase(args=[[1, 3, 5, 7], 8], expected=4),
    TemplateCase(args=[[1, 3, 5, 7], 0], expected=0),
    TemplateCase(args=[[2], 2], expected=0),
]


def search(code: str = FORM):
    return template(code, cases=CASES, harness=[])


def test_each_item_blanks_a_different_line_of_the_form():
    built = key_lines(search(), now=NOW)

    assert 1 <= len(built) <= 3
    assert len({one.line for one in built}) == len(built)


def test_the_form_s_own_line_is_one_choice_and_passes():
    for one in key_lines(search(), now=NOW):
        (right,) = [choice for choice in one.choices if choice.correct]
        assert right.text == one.code.splitlines()[one.line - 1].strip()


def test_every_other_choice_fails_a_case_it_names():
    """A choice every case passes could be a second right answer."""
    for one in key_lines(search(), now=NOW):
        for choice in one.choices:
            if choice.correct:
                continue
            assert choice.outcome in (CaseOutcome.WRONG, CaseOutcome.CRASHED)
            assert choice.case_args is not None
            assert choice.returned != choice.case_expected


def test_a_line_one_mutant_gets_wrong_is_not_blanked():
    """Two lines to choose between is a coin a guess flips."""
    # the toy form of the judging tests carries one killing mutant per line
    assert key_lines(template(), now=NOW) == []


def test_no_choice_is_wider_than_the_column():
    for one in key_lines(search(), now=NOW):
        assert all(len(choice.text) <= WIDTH for choice in one.choices)


def test_two_choices_reading_the_same_are_refused():
    right = KeyLineChoice(text="x = 1", correct=True)
    wrong = KeyLineChoice(
        text="x = 2", correct=False, change="1 -> 2", case_args=[], outcome=CaseOutcome.WRONG
    )

    with pytest.raises(ValueError, match="read the same"):
        KeyLineItem(
            id="k",
            created_at=NOW,
            template_id="t",
            form_digest="d",
            code="x = 1\n",
            line=1,
            choices=[right, wrong, wrong],
        )


def test_a_build_leaves_a_template_served_at_its_code_alone():
    first, _ = build_key_lines([card(search())], [], now=NOW)

    assert first
    assert build_key_lines([card(search())], first, now=NOW) == ([], [])


def test_items_are_stored_with_their_choices_and_retired_by_status(database):
    (held,) = seeded(
        database,
        card_record(
            templates=[
                template_record(
                    "search", code=FORM, cases=[c.model_dump() for c in CASES], harness=[]
                )
            ]
        ),
    )
    store = KeyLineStore(database)
    added, _ = build_key_lines([held], [], now=NOW)
    store.add(added)

    store.retire([added[0].id])

    assert {one.id: one.choices for one in store.all()} == {one.id: one.choices for one in added}
    assert {one.id: one.status for one in store.all()}[added[0].id] is ItemStatus.RETIRED
