from datetime import UTC, datetime, timedelta

import pytest

from climb.calls import CallLog, Reply, ask
from climb.caps import CALLS_PER_DAY, TooOften
from climb.log import erased, named, whole_log
from climb.schema import Call, Configuration

USER = "u-4f9c2a"
OTHER = "u-b71e03"
NOW = datetime.now(UTC)


def call(n: int, *, user_id: str | None, at: datetime = NOW) -> Call:
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


class Answering:
    def __init__(self) -> None:
        self.sent = 0

    def __call__(self, **_) -> Reply:
        self.sent += 1
        return Reply(text="ok", stop_reason="stop")


@pytest.fixture
def log(database):
    for user_id in (USER, OTHER):
        named(database, user_id)
    return CallLog(database)


def asked(log: CallLog, transport: Answering, user_id: str | None) -> Call:
    configuration = Configuration(model="m", effort="low", pin="a-host")
    made, _ = ask(
        transport, log, system="s", content="c", configuration=configuration, user_id=user_id
    )
    return made


def test_the_call_past_the_day_s_cap_is_refused_unsent_with_its_message(log):
    """The 51st call a user's requests make inside a day is refused before it
    reaches the model, naming the cap and its window."""
    for n in range(CALLS_PER_DAY - 1):
        log.append(call(n, user_id=USER))
    transport = Answering()
    assert asked(log, transport, USER).user_id == USER

    with pytest.raises(TooOften, match="^50 model calls a day is the cap$"):
        asked(log, transport, USER)
    assert transport.sent == 1
    assert log.made_by(USER, NOW - timedelta(days=1)) == CALLS_PER_DAY


def test_only_the_user_s_own_calls_of_the_last_day_count(log):
    """A `climb` run's calls name no account, another user's are theirs, and a
    call a day old has left the window."""
    for n in range(CALLS_PER_DAY):
        log.append(call(n, user_id=None))
        log.append(call(n, user_id=OTHER))
        log.append(call(n, user_id=USER, at=NOW - timedelta(days=1, seconds=1)))

    assert asked(log, Answering(), USER).response == "ok"


def test_a_climb_run_is_never_capped(log):
    """The author's generation and evals name no account, so no count holds
    them."""
    for n in range(CALLS_PER_DAY):
        log.append(call(n, user_id=None))

    assert asked(log, Answering(), None).user_id is None


def test_a_user_s_calls_are_exported_and_erased_with_the_log(log, database):
    """A call made for the user's request is part of the user's log, so the
    export carries it and the erasure takes it."""
    log.append(call(1, user_id=USER))
    log.append(call(1, user_id=OTHER))

    assert [one.user_id for one in whole_log(database, USER).calls] == [USER]
    assert erased(database, USER)["calls"] == 1
    assert log.made_by(USER, NOW - timedelta(days=1)) == 0
    assert log.made_by(OTHER, NOW - timedelta(days=1)) == 1
