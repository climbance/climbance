import pytest
from helpers import T0, browsing, make_problem, seed_problem

from climb.api.attention import AttentionFlag, attention_flags
from climb.log import RetirementRequestLog
from climb.problems import ProblemStore
from climb.ratings import RatingLog
from climb.schema import DifficultyRating, RetirementReason, RetirementRequest


@pytest.fixture
def author(database):
    client = browsing(database, "local")
    client.app.state.dev_user = "local"
    return client


def rate(database, problem_id: str, score: float) -> None:
    RatingLog(database).append(
        DifficultyRating(
            id=f"r-{problem_id}", created_at=T0, problem_id=problem_id, score=score, source="user"
        )
    )


def flags(author) -> dict[str, list[str]]:
    rows = author.get("/api/author/problems").json()["problems"]
    return {one["problem_id"]: one["flags"] for one in rows}


def test_a_problem_no_claim_tags_is_untagged(database, author):
    """`untagged`: the derived techniques are empty."""
    seed_problem(database, id="p1", techniques=[])
    seed_problem(database, id="p2", techniques=["greedy"])
    rate(database, "p1", 1000.0)
    rate(database, "p2", 1000.0)

    assert flags(author) == {"p1": ["untagged"], "p2": []}


def test_a_title_holding_a_technique_s_words_in_order_is_titled(database, author):
    """`titled`: the slug's words in order, case ignored, whole words only."""
    for id, title in [
        ("p1", "The Sliding Window Maximum"),
        ("p2", "Window sliding"),
        ("p3", "Heapsort cost"),
    ]:
        seed_problem(database, id=id, techniques=["greedy"], title=title)
        rate(database, id, 1000.0)

    assert flags(author) == {"p1": ["titled"], "p2": [], "p3": []}


def test_a_problem_with_no_standing_score_is_unrated(database, author):
    """`unrated`: the standing difficulty carries no score."""
    seed_problem(database, id="p1", techniques=["greedy"], difficulty="easy")

    assert flags(author) == {"p1": ["unrated"]}


def test_a_user_score_outside_the_label_s_band_is_off_band(database, author):
    """`off-band`: a `user` rating reads as deviation zero, so one point out is
    off; the band's own edge is not."""
    seed_problem(database, id="p1", techniques=["greedy"], difficulty="medium")
    seed_problem(database, id="p2", techniques=["greedy"], difficulty="medium")
    rate(database, "p1", 1099.0)
    rate(database, "p2", 1100.0)

    assert flags(author) == {"p1": ["off-band"], "p2": []}


def test_a_judge_score_within_its_deviation_of_the_band_is_not_off_band():
    """`off-band`: the score lies more than its deviation outside the band."""

    def judged(score: float) -> DifficultyRating:
        return DifficultyRating(
            id="r1",
            created_at=T0,
            problem_id="p1",
            score=score,
            deviation=150.0,
            source="judge",
            correction_id="c1",
            draw_ids=["d1"],
        )

    problem = make_problem("p1", techniques=["greedy"])
    read = [
        attention_flags(problem, generator="hard", rating=judged(score), requests=0, codes=[])
        for score in (1750.0, 1749.0)
    ]

    assert read == [[], [AttentionFlag.OFF_BAND]]


def test_a_served_problem_a_request_waits_on_is_requested(database, author):
    """`requested`: a request waits while its problem is served, so a retired
    problem's request raises none."""
    for id in ("p1", "p2"):
        seed_problem(database, id=id, techniques=["greedy"])
        rate(database, id, 1000.0)
        RetirementRequestLog(database).append(
            RetirementRequest(
                id=f"q-{id}",
                created_at=T0,
                user_id="local",
                problem_id=id,
                reason=RetirementReason.DEFECTIVE,
                note="the cases miss n = 0",
            )
        )
    ProblemStore(database).retire("p2", RetirementReason.DEFECTIVE)

    assert flags(author) == {"p1": ["requested"], "p2": []}


def test_a_flag_is_read_from_the_log_and_never_stored(database, author):
    """A rating appended later clears `unrated` with no write to the problem."""
    seed_problem(database, id="p1", techniques=["greedy"], difficulty="easy")
    before = flags(author)
    stored = ProblemStore(database).get("p1")
    rate(database, "p1", 1000.0)

    assert (before, flags(author)) == ({"p1": ["unrated"]}, {"p1": []})
    assert ProblemStore(database).get("p1") == stored
    assert "flags" not in type(stored).model_fields
