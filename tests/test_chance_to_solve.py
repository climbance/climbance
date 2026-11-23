import random
from datetime import UTC, datetime, timedelta

import pytest
from helpers import PROVENANCE, make_problem, seed_problem

from climb.board.ability import Sat, abilities, chance, practised, weakest
from climb.cases import CaseLog
from climb.cold import serve_cold, submit_cold
from climb.glicko import START, START_DEVIATION, Rated
from climb.log import SittingStore
from climb.measured import GAPS, chance_loss, held_out, loss, measured, technique_chance
from climb.mint import case, user_rating
from climb.ratings import RatingLog
from climb.schema import Attempt
from climb.sitting import end

T0 = datetime(2026, 11, 2, 10, tzinfo=UTC)
DAY = timedelta(days=1)
USER = "u-4f9c2a"
START_AT = Rated(rating=START, deviation=START_DEVIATION)
SCORES = {"p1": Rated(rating=1500.0, deviation=0.0)}
DOUBLE = "def solve(n):\n    return n * 2\n"


def sat(day: int, score: float, *, cold: bool, problem: str = "p1") -> Sat:
    return Sat(
        day=(T0 + day * DAY).date(),
        problem_id=problem,
        techniques=frozenset({"greedy"}),
        score=score,
        cold=cold,
    )


def test_a_technique_no_sitting_reached_reads_the_start():
    """An even problem at the start is an even chance, and as unsure."""
    found = chance({}, START_AT, "greedy", Rated(rating=START, deviation=0.0))

    assert (found.chance, found.deviation, found.games) == (0.5, START_DEVIATION, 0)


def test_a_practice_solve_raises_the_ability_less_than_a_cold_one():
    """A practice game is against the problem's score minus the gap."""
    practice = abilities([sat(0, 1.0, cold=False)], SCORES, START_AT, T0)["greedy"][0]
    cold = abilities([sat(0, 1.0, cold=True)], SCORES, START_AT, T0)["greedy"][0]

    assert START < practice.rating < cold.rating


def test_a_practice_miss_lowers_the_ability_more_than_a_cold_one():
    """Missing an easier opponent says more against the solver."""
    practice = abilities([sat(0, 0.0, cold=False)], SCORES, START_AT, T0)["greedy"][0]
    cold = abilities([sat(0, 0.0, cold=True)], SCORES, START_AT, T0)["greedy"][0]

    assert practice.rating < cold.rating < START


def test_a_sitting_on_a_problem_with_no_score_is_no_game():
    """A problem labelled by the generator alone has no opponent rating."""
    assert abilities([sat(0, 1.0, cold=True, problem="unrated")], SCORES, START_AT, T0) == {}


def test_more_sittings_narrow_the_deviation():
    """The reader of a chance needs to know how sure it is."""
    two = abilities([sat(n, 0.5, cold=True) for n in range(2)], SCORES, START_AT, T0 + DAY)
    forty = abilities([sat(n, 0.5, cold=True) for n in range(40)], SCORES, START_AT, T0 + 40 * DAY)

    assert forty["greedy"][0].deviation < two["greedy"][0].deviation
    assert (two["greedy"][1], forty["greedy"][1]) == (2, 40)


def test_a_problem_s_chance_is_its_weakest_technique_s():
    """A solver missing one technique a problem needs fails the problem."""
    strong = Rated(rating=1900.0, deviation=60.0)
    weak = Rated(rating=1300.0, deviation=60.0)
    held = {"greedy": (strong, 9), "graphs": (weak, 9)}
    score = Rated(rating=1500.0, deviation=0.0)

    found = weakest(held, START_AT, ["greedy", "graphs"], score)

    assert found is not None and found == chance(held, START_AT, "graphs", score)


def test_a_practice_sitting_scores_as_execution_does():
    """A solve after a failed submission counts half, and a cold sitting's
    attempts are left to the cold reading."""
    problems = {"p1": make_problem("p1", techniques=["greedy"])}
    attempts = [
        Attempt(
            id="a", user_id=USER, problem_id="p1", sitting_id="s", finished_at=T0, solved=False
        ),
        Attempt(id="b", user_id=USER, problem_id="p1", sitting_id="s", finished_at=T0, solved=True),
        Attempt(id="c", user_id=USER, problem_id="p1", sitting_id="c", finished_at=T0, solved=True),
    ]

    found = practised(attempts, problems, {}, {}, {"c"}, T0)

    assert [(one.score, one.cold) for one in found] == [(0.5, False)]


def rated(root, problem_id, techniques, score=1500.0):
    seed_problem(root, id=problem_id, techniques=techniques)
    CaseLog(root).append(case(problem_id, [3], 6, provenance=PROVENANCE))
    RatingLog(root).append(user_rating(problem_id, score))


def cold_solve(root, at):
    seated = serve_cold(root, user_id=USER, now=at, draw=random.Random(0))
    submit_cold(root, seated.sitting.id, DOUBLE, user_id=USER, now=at + timedelta(minutes=5))
    end(SittingStore(root), seated.sitting.id, user_id=USER, now=at + timedelta(minutes=6))


def test_the_engine_returns_a_technique_s_chance_and_its_deviation(database):
    """A cold solve counts for the problem's technique and its parent, and the
    start is the measured rating."""
    rated(database, "p1", ["knapsack"])
    cold_solve(database, T0)
    at = T0 + timedelta(hours=1)

    child = technique_chance(database, USER, ["knapsack"], 1500.0, at=at)
    parent = technique_chance(database, USER, ["dynamic-programming"], 1500.0, at=at)
    untouched = technique_chance(database, USER, ["greedy"], 1500.0, at=at)

    assert child is not None and parent is not None and untouched is not None
    assert child.games == parent.games == 1 and child.chance > 0.5
    assert child.deviation < START_DEVIATION
    assert untouched.games == 0 and untouched.ability == measured(database, USER, at).rating


def test_a_fit_on_no_sitting_keeps_the_starting_gap():
    """The gap moves only on the cold sittings' log-loss."""
    assert held_out([], GAPS) == (None, 200.0)


def test_each_sitting_is_scored_at_the_gap_fitted_on_the_others():
    """A score read on the sittings the gap was fitted to would understate the
    error."""
    gaps = (0.0, 200.0)
    rows = [[0.1, 0.5], [0.1, 0.5], [0.9, 0.2]]

    found, gap = held_out(rows, gaps)

    assert gap == 0.0
    assert found == pytest.approx((0.5 + 0.5 + 0.9) / 3)


def test_a_certain_miss_costs_a_finite_loss():
    """A chance of 1 on a miss would sink every other sitting's score."""
    assert loss(1.0, 0.0) < 14 and loss(0.5, 1.0) == pytest.approx(0.6931, abs=1e-4)


def test_the_score_replays_each_chance_from_before_its_sitting(database):
    """A second cold solve is predicted from the first alone, and the first
    from the start."""
    rated(database, "p1", ["knapsack"])
    rated(database, "p2", ["knapsack"])
    cold_solve(database, T0)
    cold_solve(database, T0 + DAY)

    found = chance_loss(database, gaps=(200.0,), at=T0 + 2 * DAY)
    first = technique_chance(database, USER, ["knapsack"], 1500.0, at=T0)
    second = technique_chance(database, USER, ["knapsack"], 1500.0, at=T0 + DAY)

    assert first is not None and second is not None
    assert (found.sittings, found.users) == (2, 1)
    assert found.log_loss == pytest.approx((loss(first.chance, 1) + loss(second.chance, 1)) / 2)
