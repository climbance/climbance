from datetime import timedelta

import pytest
from helpers import browsing
from test_chance_to_solve import T0, cold_solve, rated

from climb.glicko import START, START_DEVIATION, Rated
from climb.projected import ContestProblem, contest, project, projected

USER = "u-4f9c2a"
SURE = Rated(rating=1500.0, deviation=0.0)


def problem(rating: float, *needs: tuple[str, ...], count: int = 1) -> ContestProblem:
    return ContestProblem(rating=rating, needs=needs, count=count)


CONTEST = [
    problem(1000, ("greedy",)),
    problem(1600, ("greedy",), ("math",)),
    problem(2200, ("dynamic-programming",)),
    problem(2600),
]


def sure(rating: float) -> Rated:
    return Rated(rating=rating, deviation=0.0)


def test_equal_abilities_project_that_ability():
    """A user equally able in every technique projects that ability."""
    held = {t: sure(1700) for t in ("greedy", "math", "dynamic-programming")}

    found = project(held, sure(1700), CONTEST)

    assert found.rating == pytest.approx(1700, abs=0.01)
    assert found.deviation == pytest.approx(0, abs=0.01)


def test_a_stronger_technique_raises_the_projection():
    """Expected solves rise with any one technique's ability."""
    even = project({}, SURE, CONTEST)
    strong = project({"dynamic-programming": sure(2100)}, SURE, CONTEST)

    assert strong.rating > even.rating


def test_a_problem_reads_its_weakest_need():
    """Raising one of two needs leaves the problem at the other."""
    only = [problem(1600, ("greedy",), ("math",))]

    found = project({"greedy": sure(2400)}, SURE, only)

    assert found.rating == pytest.approx(1500, abs=0.01)


def test_a_need_is_met_by_its_strongest_technique():
    """A tag naming two searches needs either one."""
    only = [problem(1600, ("breadth-first-search", "depth-first-search"))]

    found = project({"depth-first-search": sure(1900)}, SURE, only)

    assert found.rating == pytest.approx(1900, abs=0.01)


def test_a_problem_naming_no_technique_reads_the_start():
    """The engine predicts nothing finer for it than the start."""
    found = project({"greedy": sure(2400)}, sure(1300), [problem(2600)])

    assert found.rating == pytest.approx(1300, abs=0.01)


def test_wider_abilities_widen_the_projection():
    """The deviation is the projection's spread over draws of the abilities."""
    narrow = project({}, Rated(rating=1500, deviation=60), CONTEST)
    wide = project({}, Rated(rating=1500, deviation=300), CONTEST)

    assert 0 < narrow.deviation < wide.deviation
    assert project({}, Rated(rating=1500, deviation=60), CONTEST) == narrow


def test_the_contest_holds_the_window_s_rated_problems():
    """593 rated problems in 101 rounds, as the distribution counted."""
    assert sum(one.count for one in contest()) == 593


def test_a_new_user_projects_the_start(database):
    """With no sitting, every technique is the start, and as unsure."""
    found = projected(database, USER)

    assert found.rating == pytest.approx(START, abs=0.01)
    assert found.deviation == pytest.approx(START_DEVIATION, rel=0.1)
    assert found.techniques == 0


def test_a_cold_solve_raises_the_projection(database):
    """The projection reads the same abilities the chance to solve does."""
    rated(database, "p1", ["greedy"], score=1800.0)
    cold_solve(database, T0)

    found = projected(database, USER, T0 + timedelta(hours=1))

    assert found.rating > START
    assert found.techniques >= 1


def test_the_route_returns_the_projection_and_its_deviation(database):
    """A new user's projection is the start, as the function's is."""
    found = browsing(database, USER).get("/api/projection").json()

    assert found["rating"] == pytest.approx(START, abs=0.01)
    assert found["deviation"] > 0


def test_the_techniques_count_those_the_contest_needs():
    """A technique no contest problem needs moves nothing, so is not counted."""
    found = project({"greedy": sure(1600), "knapsack-unused": sure(1600)}, SURE, CONTEST)

    assert found.techniques == 1
