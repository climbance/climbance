from datetime import UTC, datetime, timedelta

from helpers import a_call
from sqlalchemy import insert, text

from climb.api.spend_figures import UNCITED, spend_figures
from climb.calls import CallLog
from climb.log.table import diagnoses
from climb.ratings.table import difficulty_draws

NOW = datetime(2026, 11, 23, 12, tzinfo=UTC)


def replica(database, *rows) -> None:
    # rows whose foreign keys name nothing the figure reads
    with database.engine.begin() as conn:
        conn.execute(text("SET LOCAL session_replication_role = replica"))
        for table, values in rows:
            conn.execute(insert(table).values(**values))


def test_an_empty_call_log_spends_nothing(database):
    """No call in the period reads no row and no uncosted call."""
    read = spend_figures(database, NOW)

    assert (read.spend, read.uncosted) == ([], 0)


def test_spend_reads_by_the_part_citing_each_call(database):
    """An uncited call reads as uncited, and a call with no cost is counted."""
    calls = CallLog(database)
    at = NOW - timedelta(days=1)
    for id, cost in (("c-judge", 0.5), ("c-judge-2", 0.25), ("c-diag", None), ("c-lost", 0.08)):
        calls.append(a_call(id, created_at=at, cost=cost))
    draw = {"created_at": at, "problem_id": "p", "judged": 1500}
    replica(
        database,
        (difficulty_draws, draw | {"id": "d1", "call_id": "c-judge"}),
        (difficulty_draws, draw | {"id": "d2", "call_id": "c-judge-2"}),
        (
            diagnoses,
            {
                "id": "g1",
                "created_at": at,
                "attempt_id": "a",
                "cause": "slip",
                "evidence": "e",
                "call_id": "c-diag",
            },
        ),
    )

    read = spend_figures(database, NOW)

    assert [(one.part, one.calls, one.cost) for one in read.spend] == [
        ("difficulty · judge", 2, 0.75),
        ("diagnoser", 1, 0.0),
        (UNCITED, 1, 0.08),
    ]
    assert read.uncosted == 1


def test_a_call_before_the_period_is_left_out(database):
    """The spend covers the last 30 days alone."""
    CallLog(database).append(a_call("c-old", created_at=NOW - timedelta(days=31), cost=1.0))

    assert spend_figures(database, NOW).spend == []
