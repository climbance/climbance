from datetime import UTC, datetime, timedelta

import pytest

from climb.caps import RUNS_PER_HOUR, RUNS_PER_MINUTE, TooOften, capped

AT = datetime(2026, 11, 17, 10, tzinfo=UTC)


def started(minute: int, hour: int):
    return lambda since: minute if AT - since <= timedelta(minutes=1) else hour


def test_runs_under_both_caps_stand():
    """A run is refused only past a cap, never at the run before it."""
    capped(started(RUNS_PER_MINUTE - 1, RUNS_PER_HOUR - 1), AT, "recalls")


def test_the_hour_refuses_what_the_minute_admits():
    """The two windows are checked apart, so a slow steady stream still meets
    the hour's cap."""
    with pytest.raises(TooOften, match="60 recalls an hour is the cap"):
        capped(started(0, RUNS_PER_HOUR), AT, "recalls")


def test_the_minute_names_itself():
    """The refusal names the window it broke, so the user knows how long to
    wait."""
    with pytest.raises(TooOften, match="10 submissions a minute is the cap"):
        capped(started(RUNS_PER_MINUTE, RUNS_PER_MINUTE), AT, "submissions")
