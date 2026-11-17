from datetime import timedelta

import pytest
from helpers import T0, make_problem
from pydantic import ValidationError

from climb.mint import user_rating
from climb.problems import ProblemStore
from climb.ratings import RatingLog, with_standing_difficulty
from climb.schema import BANDS, DifficultyRating, ProblemDifficulty, band
from climb.solution_claims import load_problem, load_problems

EASY, MEDIUM, HARD = ProblemDifficulty.EASY, ProblemDifficulty.MEDIUM, ProblemDifficulty.HARD
SCORE = {EASY: 1000.0, MEDIUM: 1600.0, HARD: 2400.0}


def rating(label, *, source="user", at=0, problem_id="p1") -> DifficultyRating:
    fitted = {"fit_id": "f1", "deviation": 80.0} if source == "fit" else {}
    return DifficultyRating(
        id=f"r-{source}-{at}",
        created_at=T0 + timedelta(minutes=at),
        problem_id=problem_id,
        score=SCORE[label],
        source=source,
        **fitted,
    )


def standing(problem, ratings) -> ProblemDifficulty | None:
    (rated,) = with_standing_difficulty([problem], ratings)
    return rated.difficulty


def test_an_unrated_problem_keeps_the_generators_label():
    assert standing(make_problem(difficulty=EASY), []) is EASY


def test_the_latest_rating_stands():
    """A rating is superseded by appending another, never by rewriting one."""
    ratings = [rating(HARD, at=0), rating(MEDIUM, at=1)]

    assert standing(make_problem(difficulty=EASY), ratings) is MEDIUM


def test_the_users_rating_stands_over_a_later_fit():
    ratings = [rating(MEDIUM, at=0), rating(HARD, source="fit", at=5)]

    assert standing(make_problem(difficulty=EASY), ratings) is MEDIUM


def test_a_rating_of_another_problem_moves_nothing():
    ratings = [rating(HARD, problem_id="p2")]

    assert standing(make_problem(difficulty=EASY), ratings) is EASY


def test_a_band_starts_at_its_cut():
    """A score on a cut takes the higher label: each cut is a band's floor."""
    cuts = [low for low, _ in BANDS[1:]]

    assert [band(cut - 1) for cut in cuts] == [EASY, MEDIUM]
    assert [band(cut) for cut in cuts] == [MEDIUM, HARD]


@pytest.mark.parametrize(
    "fields",
    [
        {"source": "fit", "deviation": 80.0},
        {"source": "fit", "fit_id": "f1"},
        {"source": "user", "fit_id": "f1"},
        {"source": "user", "deviation": 80.0},
    ],
)
def test_a_fit_and_only_a_fit_names_its_fit_and_deviation(fields):
    with pytest.raises(ValidationError):
        DifficultyRating(id="r1", created_at=T0, problem_id="p1", score=1500.0, **fields)


def test_the_loaders_serve_the_standing_difficulty(database):
    """Every reader of a label loads through these, so a rating reaches the
    badge, the listing's filter and the selector at once."""
    ProblemStore(database).put(make_problem(difficulty=EASY))
    RatingLog(database).append(user_rating("p1", SCORE[HARD]))

    (every,) = load_problems(database)
    one = load_problem(database, "p1")

    assert (every.difficulty, one.difficulty if one else None) == (HARD, HARD)
    assert ProblemStore(database).get("p1").difficulty is EASY
