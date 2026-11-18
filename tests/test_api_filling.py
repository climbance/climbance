from datetime import UTC, datetime

import pytest
from helpers import browsing
from matching import card, seeded, template
from test_key_lines import CASES, FORM, RANGE, RANGE_CASES

from climb.judging import build_key_lines
from climb.keylines import KeyLineStore
from climb.log import FillLog

USER = "u-4f9c2a"


@pytest.fixture
def client(database):
    (held,) = seeded(
        database,
        card(
            slug="search",
            templates=[
                template("search", code=FORM, cases=[c.model_dump() for c in CASES], harness=[])
            ],
        ),
    )
    added, _ = build_key_lines([held], [], now=datetime(2026, 11, 16, tzinfo=UTC))
    KeyLineStore(database).add(added)
    return browsing(database, USER)


def test_an_item_is_served_with_its_line_blank_and_no_answer(client, database):
    """No field says which choice is right before the fill."""
    served = client.get("/api/filling/next").json()

    (item,) = [one for one in KeyLineStore(database).all() if one.id == served["item_id"]]
    assert served["lines"][item.line - 1].strip() == ""
    assert served["blank"] == served["blank_end"] == item.line
    assert sorted(one["text"] for one in served["choices"]) == sorted(
        one.text for one in item.choices
    )
    assert all(set(one) == {"choice", "text"} for one in served["choices"])


def test_the_form_s_own_line_fills_right(client, database):
    item = KeyLineStore(database).all()[0]
    right = next(at for at, one in enumerate(item.choices) if one.correct)

    decided = client.post(f"/api/filling/{item.id}", json={"choice": right}).json()

    assert decided == {"right": True, "line": item.choices[right].text, "case": None}
    assert [one.choice for one in FillLog(database).for_user(USER)] == [right]


def test_a_wrong_choice_shows_its_separating_case(client, database):
    item = KeyLineStore(database).all()[0]
    wrong = next(at for at, one in enumerate(item.choices) if not one.correct)

    decided = client.post(f"/api/filling/{item.id}", json={"choice": wrong}).json()

    assert decided["right"] is False
    assert decided["case"]["args"] == item.choices[wrong].case_args


def test_a_fill_moves_the_pick_to_an_unseen_item(client, database):
    first = client.get("/api/filling/next").json()["item_id"]
    client.post(f"/api/filling/{first}", json={"choice": 0})

    assert client.get("/api/filling/next").json()["item_id"] != first


def test_a_choice_the_item_lacks_is_refused(client, database):
    item = KeyLineStore(database).all()[0]

    assert client.post(f"/api/filling/{item.id}", json={"choice": 9}).status_code == 422
    assert FillLog(database).for_user(USER) == []


def test_a_statement_spanning_two_lines_is_served_blank_on_both(database):
    """The blank covers the whole statement, so no choice reads as half."""
    (held,) = seeded(
        database,
        card(
            slug="range",
            templates=[
                template(
                    "range", code=RANGE, cases=[c.model_dump() for c in RANGE_CASES], harness=[]
                )
            ],
        ),
    )
    added, _ = build_key_lines([held], [], now=datetime(2026, 11, 16, tzinfo=UTC))
    KeyLineStore(database).add([one for one in added if one.line == 4])

    served = browsing(database, USER).get("/api/filling/next").json()

    assert (served["blank"], served["blank_end"]) == (4, 5)
    assert served["lines"][3:5] == ["        ", ""]
