"""How many runs of one kind a user may start: `docs/architecture/README.md`."""

from collections.abc import Callable
from datetime import datetime, timedelta

# each window and the runs of one kind a user may start inside it. The broker
# admits one run at a time, so a burst is every other user's wait
RUN_CAPS = ((timedelta(minutes=1), 10, "a minute"), (timedelta(hours=1), 60, "an hour"))
RUNS_PER_MINUTE, RUNS_PER_HOUR = (most for _, most, _ in RUN_CAPS)


class TooOften(ValueError):
    """More runs of one kind in a window than its cap allows."""


def capped(started_since: Callable[[datetime], int], at: datetime, kind: str) -> None:
    """Refuse a run past any window's cap, given how many the user started since
    a moment."""
    for window, most, per in RUN_CAPS:
        if started_since(at - window) >= most:
            raise TooOften(f"{most} {kind} {per} is the cap")
