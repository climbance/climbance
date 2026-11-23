import random
from datetime import UTC, datetime, timedelta

from helpers import PROVENANCE, browsing, stored_problem

from climb.cases import CaseLog
from climb.cold import serve_cold, submit_cold
from climb.glicko import START, START_DEVIATION
from climb.log import SittingStore
from climb.measured import chance, measured
from climb.mint import case, user_rating
from climb.ratings import RatingLog
from climb.sitting import end

DAY = datetime(2026, 11, 23, 10, tzinfo=UTC)
USER = "u-4f9c2a"
DOUBLE = "def solve(n):\n    return n * 2\n"


def rated(root, problem_id, score=1500.0):
    stored_problem(root, problem_id)
    CaseLog(root).append(case(problem_id, [3], 6, provenance=PROVENANCE))
    RatingLog(root).append(user_rating(problem_id, score))


def sat(root, at, *, solved):
    seated = serve_cold(root, user_id=USER, now=at, draw=random.Random(0))
    if solved:
        submit_cold(root, seated.sitting.id, DOUBLE, user_id=USER, now=at + timedelta(minutes=5))
    end(SittingStore(root), seated.sitting.id, user_id=USER, now=at + timedelta(minutes=6))


def test_a_user_with_no_cold_sitting_starts_at_the_defaults(database):
    found = measured(database, USER, DAY)

    assert (found.rating, found.deviation, found.games) == (START, START_DEVIATION, 0)


def test_a_solve_raises_the_rating_and_a_miss_lowers_it(database):
    """Each ended cold sitting is one game against the problem's score."""
    rated(database, "p1")
    rated(database, "p2")
    sat(database, DAY, solved=True)
    after_win = measured(database, USER, DAY + timedelta(hours=1))
    sat(database, DAY + timedelta(days=1), solved=False)
    after_loss = measured(database, USER, DAY + timedelta(days=1, hours=1))

    assert after_win.games == 1 and after_win.rating > START
    assert after_win.deviation < START_DEVIATION
    assert after_loss.games == 2 and after_loss.rating < after_win.rating


def test_a_running_cold_sitting_is_no_game_yet(database):
    """Its outcome is not decided."""
    rated(database, "p1")
    serve_cold(database, user_id=USER, now=DAY, draw=random.Random(0))

    assert measured(database, USER, DAY + timedelta(minutes=5)).games == 0


def test_a_replay_reads_the_score_as_it_stands_now(database):
    """A later rating of the problem corrects the game played against it."""
    rated(database, "p1", score=1200.0)
    sat(database, DAY, solved=True)
    before = measured(database, USER, DAY + timedelta(hours=1))

    RatingLog(database).append(user_rating("p1", 2000.0))
    after = measured(database, USER, DAY + timedelta(hours=1))

    assert after.rating > before.rating


def test_the_chance_is_lower_on_a_harder_problem(database):
    rated(database, "p1", score=1200.0)
    rated(database, "p2", score=2000.0)

    easy = chance(database, USER, "p1", DAY)
    hard = chance(database, USER, "p2", DAY)

    assert easy is not None and hard is not None
    assert easy > 0.5 > hard


def test_the_chance_of_an_unscored_problem_is_none(database):
    stored_problem(database, "p1")

    assert chance(database, USER, "p1", DAY) is None


def test_the_route_returns_the_rating_its_deviation_and_the_games(database):
    rated(database, "p1")
    sat(database, datetime.now(UTC) - timedelta(hours=2), solved=True)

    found = browsing(database, USER).get("/api/rating").json()

    assert found["games"] == 1
    assert found["rating"] > START
    assert found["deviation"] < START_DEVIATION
