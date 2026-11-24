"""How many runs of one kind a user may start, and how many model calls a user's
requests may make: `api/submission.md`, `api/README.md`."""

from collections.abc import Callable
from datetime import datetime, timedelta

# each window and the runs of one kind a user may start inside it. The broker
# admits one run at a time, so a burst is every other user's wait
RUN_CAPS = ((timedelta(minutes=1), 10, "a minute"), (timedelta(hours=1), 60, "an hour"))
RUNS_PER_MINUTE, RUNS_PER_HOUR = (most for _, most, _ in RUN_CAPS)
# one user's calls may not spend every other user's share of the model budget
CALLS_PER_DAY = 50
CALL_CAPS = ((timedelta(days=1), CALLS_PER_DAY, "a day"),)


class TooOften(ValueError):
    """More runs of one kind in a window than its cap allows."""


def capped(
    started_since: Callable[[datetime], int],
    at: datetime,
    kind: str,
    caps: tuple[tuple[timedelta, int, str], ...] = RUN_CAPS,
) -> None:
    """Refuse a run past any window's cap, given how many the user started since
    a moment."""
    for window, most, per in caps:
        if started_since(at - window) >= most:
            raise TooOften(f"{most} {kind} {per} is the cap")


def calls_capped(made_since: Callable[[datetime], int], at: datetime) -> None:
    """Refuse a model call a user's request would make past the day's cap."""
    capped(made_since, at, "model calls", CALL_CAPS)
