from datetime import UTC, date, datetime, timedelta

from helpers import attempt, authoring, seed_problem, stored_problem, stored_template
from sqlalchemy import insert, text

from climb.api.inbox_figures import Pass, inbox_figures, waiting_rows
from climb.log import AttemptLog, FeedbackLog, RetirementRequestLog, named
from climb.log.table import run_faults
from climb.schema import (
    Client,
    Feedback,
    ProblemStatus,
    RetirementReason,
    RetirementRequest,
    RunKind,
)

NOW = datetime(2026, 11, 23, 12, tzinfo=UTC)
AUTHOR = "u-4f9c2a"
LEARNER = "u-8b31d7"


def replica(database, *rows) -> None:
    # rows whose foreign keys name nothing the figure reads
    with database.engine.begin() as conn:
        conn.execute(text("SET LOCAL session_replication_role = replica"))
        for table, values in rows:
            conn.execute(insert(table).values(**values))


def waiting(read) -> dict[Pass, int | None]:
    return {one.command: one.count for one in read.waiting}


def test_an_empty_store_waits_on_nothing(database):
    """With no correction stored, `difficulty judge` reads no count."""
    read = inbox_figures(database, AUTHOR, NOW)

    assert waiting(read) == {
        Pass.CLAIM: 0,
        Pass.MATCH: 0,
        Pass.DIFFICULTY: None,
        Pass.JUDGE: 0,
        Pass.FILL: 0,
    }
    assert read.waiting_requests == read.answered_requests == read.feedback == read.faults == []


def test_the_claim_pass_counts_the_authors_attempts_alone(database):
    """The pass reads the signed-in author's log, never a learner's."""
    seed_problem(database, id="p1", techniques=["greedy", "two-pointers"])
    log = AttemptLog(database)
    for id, user_id in (("a1", AUTHOR), ("a2", LEARNER)):
        named(database, user_id)
        log.append_attempt(attempt(id, "p1").model_copy(update={"user_id": user_id}))

    assert waiting(inbox_figures(database, AUTHOR, NOW))[Pass.CLAIM] == 1


def test_a_template_with_no_items_waits_for_both_builds(database):
    stored_template(database, "t1")

    read = waiting(inbox_figures(database, AUTHOR, NOW))

    assert (read[Pass.JUDGE], read[Pass.FILL]) == (1, 1)


def test_a_request_waits_while_its_problem_is_served(database):
    """A request on a retired problem reads as answered, with the status."""
    stored_problem(database, "p1", title="Pair sums under a cap")
    stored_problem(
        database,
        "p2",
        title="Longest calm stretch",
        status=ProblemStatus.RETIRED,
        retired_reason=RetirementReason.DEFECTIVE,
    )
    named(database, LEARNER)
    log = RetirementRequestLog(database)
    for id, problem_id, day in (("r1", "p1", 9), ("r2", "p2", 22)):
        log.append(
            RetirementRequest(
                id=id,
                created_at=datetime(2026, 11, day, tzinfo=UTC),
                user_id=LEARNER,
                problem_id=problem_id,
                reason=RetirementReason.DEFECTIVE,
                note="case 4 expects the wrong sum",
            )
        )

    read = inbox_figures(database, AUTHOR, NOW)

    assert [one.title for one in read.waiting_requests] == ["Pair sums under a cap"]
    assert [(one.title, one.status) for one in read.answered_requests] == [
        ("Longest calm stretch", ProblemStatus.RETIRED)
    ]


def test_feedback_reads_newest_first(database):
    named(database, LEARNER)
    log = FeedbackLog(database)
    for id, day in (("f1", 20), ("f2", 21)):
        log.append(
            Feedback(
                id=id,
                created_at=datetime(2026, 11, day, tzinfo=UTC),
                user_id=LEARNER,
                client=Client.WEB,
                page="/knowledge/queue",
                note=f"note {id}",
            )
        )

    read = inbox_figures(database, AUTHOR, NOW)

    assert [one.note for one in read.feedback] == ["note f2", "note f1"]


def test_feedback_counts_the_notes_of_the_last_seven_days(database):
    """A note older than the week is listed and left out of the count."""
    named(database, LEARNER)
    log = FeedbackLog(database)
    for id, day in (("f1", 10), ("f2", 21)):
        log.append(
            Feedback(
                id=id,
                created_at=datetime(2026, 11, day, tzinfo=UTC),
                user_id=LEARNER,
                client=Client.WEB,
                page="/",
                note=id,
            )
        )

    read = inbox_figures(database, AUTHOR, NOW)

    assert (len(read.feedback), read.feedback_days, read.feedback_recent) == (2, 7, 1)


def test_faults_count_per_day_and_kind_over_the_period(database):
    """A fault older than the period is in neither the counts nor the list."""

    def fault(id: str, at: datetime, kind: RunKind):
        values = {"id": id, "created_at": at, "user_id": LEARNER, "kind": kind, "detail": id}
        return run_faults, values

    replica(
        database,
        fault("f1", NOW - timedelta(hours=1), RunKind.SUBMISSION),
        fault("f2", NOW - timedelta(hours=2), RunKind.SUBMISSION),
        fault("f3", NOW - timedelta(days=1), RunKind.RECALL),
        fault("f4", NOW - timedelta(days=40), RunKind.RECALL),
    )

    read = inbox_figures(database, AUTHOR, NOW)

    assert [(one.day, one.counts) for one in read.fault_days] == [
        (date(2026, 11, 23), {RunKind.SUBMISSION: 2, RunKind.RECALL: 0}),
        (date(2026, 11, 22), {RunKind.SUBMISSION: 0, RunKind.RECALL: 1}),
    ]
    assert [one.detail for one in read.faults] == ["f1", "f2", "f3"]


def test_the_route_names_no_user(database):
    """Feedback and requests are read whole, but never with who sent them."""
    named(database, LEARNER)
    FeedbackLog(database).append(
        Feedback(
            id="f1",
            created_at=NOW,
            user_id=LEARNER,
            client=Client.WEB,
            page="/",
            note="a note",
        )
    )
    client = authoring(database, "local")
    client.app.state.dev_user = "local"

    response = client.get("/api/author/inbox")

    assert response.status_code == 200
    assert LEARNER not in response.text and "a note" in response.text


def test_the_navigation_counts_the_waiting_rows_that_count_something(database):
    """Each waiting request is a row; a retired problem's request and a pass
    counting nothing add none."""
    stored_template(database, "t1")
    stored_problem(database, "p1")
    stored_problem(
        database,
        "p2",
        status=ProblemStatus.RETIRED,
        retired_reason=RetirementReason.DEFECTIVE,
    )
    named(database, LEARNER)
    log = RetirementRequestLog(database)
    for id, problem_id in (("r1", "p1"), ("r2", "p2"), ("r3", "p1")):
        log.append(
            RetirementRequest(
                id=id,
                created_at=NOW,
                user_id=LEARNER,
                problem_id=problem_id,
                reason=RetirementReason.DEFECTIVE,
                note="case 4 expects the wrong sum",
            )
        )

    assert waiting_rows(database, AUTHOR) == 4
