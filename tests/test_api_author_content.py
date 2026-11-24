from datetime import timedelta

import pytest
from helpers import PROVENANCE, T0, authoring, seed_problem
from test_api_reads import a_card
from test_difficulty_judge import a_draw, anchored

from climb.api.author_content import author_cards, author_problems
from climb.cards import CardStore
from climb.cases import CaseLog
from climb.difficulty import DRAWS, correct, rating
from climb.log import RetirementRequestLog
from climb.matches import MatchLog
from climb.mint import case
from climb.problems import ProblemStore
from climb.ratings import CorrectionLog, DrawLog, RatingLog
from climb.schema import (
    DifficultyRating,
    MatchSource,
    Requirement,
    RetirementReason,
    RetirementRequest,
    TemplateMatch,
)


@pytest.fixture
def author(database):
    client = authoring(database, "local")
    client.app.state.dev_user = "local"
    return client


def matched(template_id: str, solution_id: str) -> TemplateMatch:
    return TemplateMatch(
        id=f"m-{template_id}-{solution_id}",
        created_at=T0,
        template_id=template_id,
        solution_id=solution_id,
        matched=True,
        source=MatchSource.USER,
    )


def test_the_cards_read_in_the_graph_s_order_with_their_ladders(database, author):
    """A required card reads first, and a rung names the forms it covers."""
    root = a_card("two-pointers", "two-pointers")
    above = a_card("sliding-window", "sliding-window").model_copy(
        update={"requires": [Requirement(card="two-pointers", template="core", used_by="core")]}
    )
    CardStore(database).put_all([above, root])
    seed_problem(database, id="p1", techniques=["two-pointers"], difficulty="easy")
    MatchLog(database).append(matched("t-two-pointers", "p1-canonical"))

    cards = author.get("/api/author/cards").json()["cards"]

    assert [one["card"]["slug"] for one in cards] == ["two-pointers", "sliding-window"]
    assert cards[0]["required_by"] == [
        {"card": "sliding-window", "template": "core", "used_by": "core"}
    ]
    assert [(r["problem_id"], r["templates"], r["required"]) for r in cards[0]["rungs"]] == [
        ("p1", ["core"], True)
    ]
    assert (cards[0]["gaps"], cards[1]["gaps"]) == ([], ["core"])


def test_the_problems_list_retired_ones_with_their_counts(database, author):
    """The browser reads every problem, served or retired."""
    seed_problem(database, id="p1", techniques=["greedy"])
    seed_problem(database, id="p2", techniques=["sorting"])
    ProblemStore(database).retire("p2", RetirementReason.DEFECTIVE)
    CaseLog(database).append(case("p1", [1], 2, provenance=PROVENANCE))
    RetirementRequestLog(database).append(
        RetirementRequest(
            id="r1",
            created_at=T0,
            user_id="local",
            problem_id="p1",
            reason=RetirementReason.DEFECTIVE,
            note="the cases miss n = 0",
        )
    )

    rows = {one["problem_id"]: one for one in author.get("/api/author/problems").json()["problems"]}

    assert (rows["p1"]["cases"], rows["p1"]["requests"]) == (1, 1)
    assert (rows["p1"]["retired_reason"], rows["p2"]["retired_reason"]) == (None, "defective")


def test_a_row_reads_the_standing_judge_rating_s_deviation(database, author):
    """The row reads the score with the deviation a judge's rating names."""
    seed_problem(database, id="p1", techniques=["greedy"])
    draws, anchors = anchored()
    correction = correct(draws, anchors, anchor_set="h1")
    CorrectionLog(database).append(correction)
    mine = [a_draw("p1", 1500, n) for n in range(DRAWS)]
    for one in mine:
        DrawLog(database).append(one)
    made = rating("p1", mine, correction)
    RatingLog(database).append(made)

    [row] = author.get("/api/author/problems").json()["problems"]

    assert (row["score"], row["deviation"]) == (made.score, made.deviation)


def test_an_opened_problem_reads_its_solutions_cases_and_ratings(database, author):
    """The ratings read latest first, the standing one marked."""
    seed_problem(
        database,
        id="p1",
        techniques=["greedy"],
        difficulty="medium",
        statement="Sum.\n\ndef solve(xs):",
    )
    CaseLog(database).append(case("p1", [[1, 2]], 3, provenance=PROVENANCE))
    for at in (1, 2):
        RatingLog(database).append(
            DifficultyRating(
                id=f"r{at}",
                created_at=T0 + timedelta(minutes=at),
                problem_id="p1",
                score=1200.0 + at,
                source="user",
            )
        )

    read = author.get("/api/author/problems/p1").json()

    assert (read["statement"], read["signature"], read["generator"]) == (
        "Sum.",
        "def solve(xs):",
        "medium",
    )
    assert [(one["role"], one["claims"]) for one in read["solutions"]] == [
        ("canonical", ["greedy"])
    ]
    [one] = read["cases"]
    assert (one["args"], one["expected"], one["size"], one["round"]) == ("([1,2])", "3", 8, 0)
    assert [(one["score"], one["standing"]) for one in read["ratings"]] == [
        (1202.0, True),
        (1201.0, False),
    ]
    assert author.get("/api/author/problems/nope").status_code == 404


def test_a_card_counts_each_template_s_items_and_a_problem_names_its_target(database):
    """A template with no item of a kind waits for `climb fill build`."""
    CardStore(database).put(a_card("greedy-basic", "greedy"))
    seed_problem(
        database,
        id="p1",
        techniques=["greedy"],
        target_template_id="t-greedy-basic",
        target_technique=None,
    )

    (card,) = author_cards(database).cards
    (row,) = author_problems(database).problems

    assert (card.counts[0].keyline_items, card.required_by) == (0, [])
    assert row.target_template == "core"


def test_an_opened_problem_cuts_each_case_and_a_pressed_one_reads_whole(database, author):
    """A heavy case keeps the opened problem small, and reads whole alone."""
    seed_problem(database, id="p1", techniques=["greedy"], statement="Sum.\n\ndef solve(xs):")
    heavy = case("p1", [list(range(100_000))], 1, provenance=PROVENANCE)
    CaseLog(database).append(heavy)

    opened = author.get("/api/author/problems/p1")
    [one] = opened.json()["cases"]
    whole = author.get(f"/api/author/problems/p1/cases/{one['id']}")

    assert len(opened.content) < 50_000
    assert one["size"] > 500_000
    assert len(one["args"]) == 120
    assert whole.json() == {"args": heavy.args, "expected": 1}
    assert author.get("/api/author/problems/p2/cases/" + one["id"]).status_code == 404
