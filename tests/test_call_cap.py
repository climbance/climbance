from datetime import UTC, datetime, timedelta

import pytest

from climb.calls import CallLog
from climb.caps import CALLS_PER_DAY, TooOften, calls_capped
from climb.log import erased, named, whole_log
from climb.schema import Call

USER = "u-4f9c2a"
OTHER = "u-b71e03"
AT = datetime(2026, 11, 24, 10, tzinfo=UTC)


def call(n: int, *, user_id: str | None, at: datetime = AT) -> Call:
    return Call(
        id=f"c-{user_id}-{n}-{at.isoformat()}",
        created_at=at,
        model="m",
        effort="none",
        prompt="p",
        prompt_hash="h",
        response="r",
        user_id=user_id,
    )


@pytest.fixture
def log(database):
    for user_id in (USER, OTHER):
        named(database, user_id)
    return CallLog(database)


def made(log: CallLog, user_id: str):
    return lambda since: log.made_by(user_id, since)


def test_the_call_past_the_day_s_cap_is_refused_with_its_message(log):
    """The 51st call a user's requests make inside a day is refused, naming the
    cap and its window."""
    for n in range(CALLS_PER_DAY - 1):
        log.append(call(n, user_id=USER))
    calls_capped(made(log, USER), AT)
    log.append(call(CALLS_PER_DAY, user_id=USER))

    with pytest.raises(TooOften, match="^50 model calls a day is the cap$"):
        calls_capped(made(log, USER), AT)


def test_only_the_user_s_own_calls_of_the_last_day_count(log):
    """A `climb` run's calls name no account, another user's are theirs, and a
    call a day old has left the window."""
    for n in range(CALLS_PER_DAY):
        log.append(call(n, user_id=None))
        log.append(call(n, user_id=OTHER))
        log.append(call(n, user_id=USER, at=AT - timedelta(days=1, seconds=1)))

    calls_capped(made(log, USER), AT)


def test_a_user_s_calls_are_exported_and_erased_with_the_log(log, database):
    """A call made for the user's request is part of the user's log, so the
    export carries it and the erasure takes it."""
    log.append(call(1, user_id=USER))
    log.append(call(1, user_id=OTHER))

    assert [one.user_id for one in whole_log(database, USER).calls] == [USER]
    assert erased(database, USER)["calls"] == 1
    assert log.made_by(USER, AT) == 0
    assert log.made_by(OTHER, AT) == 1
