import pytest

from climb.glicko import GROWTH, START_DEVIATION, Game, Rated, expected, grown, updated


def rated(rating: float, deviation: float) -> Rated:
    return Rated(rating=rating, deviation=deviation)


def test_one_period_matches_glickmans_worked_example():
    """Glickman's example: 1500 at 200, a win, two losses: 1464 at 151.4."""
    games = [
        Game(opponent=rated(1400, 30), score=1),
        Game(opponent=rated(1550, 100), score=0),
        Game(opponent=rated(1700, 300), score=0),
    ]

    after = updated(rated(1500, 200), games)

    assert after.rating == pytest.approx(1464, abs=0.5)
    assert after.deviation == pytest.approx(151.4, abs=0.1)


def test_a_period_without_games_leaves_the_rating():
    assert updated(rated(1500, 200), []) == rated(1500, 200)


def test_the_deviation_grows_by_the_constant_and_stops_at_the_start():
    """An unused rating widens again, but never past a new user's."""
    assert grown(rated(1500, 50), 1).deviation == pytest.approx((50**2 + GROWTH**2) ** 0.5)
    assert grown(rated(1500, 50), 365).deviation == pytest.approx(START_DEVIATION)
    assert grown(rated(1500, 50), 10_000).deviation == START_DEVIATION


def test_an_even_match_is_a_coin_flip_and_a_wide_deviation_pulls_to_one_half():
    """The chance combines both deviations."""
    assert expected(rated(1500, 50), rated(1500, 50)) == pytest.approx(0.5)
    sure = expected(rated(1900, 30), rated(1500, 0))
    unsure = expected(rated(1900, 350), rated(1500, 0))
    assert 0.5 < unsure < sure
