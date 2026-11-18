from collections.abc import Iterable
from datetime import datetime
from operator import attrgetter
from typing import Protocol

from climb.standing import latest_by


class AttemptKeyed(Protocol):
    attempt_id: str
    created_at: datetime


def latest_by_attempt[R: AttemptKeyed](records: Iterable[R]) -> dict[str, R]:
    """One reader of the attempt-keyed records: `concepts/log-records.md`."""
    return latest_by(records, attrgetter("attempt_id"))
