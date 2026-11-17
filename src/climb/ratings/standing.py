from collections.abc import Iterable
from operator import attrgetter

from climb.schema import DifficultyRating, Problem, RatingSource
from climb.standing import standing

# weakest first: the user's rating stands over a fit's, however late
BY_WHAT_EACH_KNEW = (RatingSource.FIT, RatingSource.USER)


def standing_ratings(ratings: Iterable[DifficultyRating]) -> dict[str, DifficultyRating]:
    return standing(ratings, attrgetter("problem_id"), by_what_each_knew=BY_WHAT_EACH_KNEW)


def with_standing_difficulty(
    problems: Iterable[Problem], ratings: Iterable[DifficultyRating]
) -> list[Problem]:
    """Each problem carrying the band of its standing score; the generator's
    label where no rating exists."""
    stands = standing_ratings(ratings)
    return [
        problem.model_copy(update={"difficulty": stands[problem.id].label})
        if problem.id in stands
        else problem
        for problem in problems
    ]
