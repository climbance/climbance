from datetime import UTC, date, datetime, timedelta

from helpers import authoring
from sqlalchemy import insert, text

from climb.api.product_figures import product_figures
from climb.knowledge.table import answers
from climb.log import Provider, Role, invite, named, signed_in
from climb.log.table import attempts, fills, sittings

NOW = datetime(2026, 11, 23, 12, tzinfo=UTC)
LEARNER = "u-4f9c2a"
OTHER = "u-8b31d7"


def acted(database, user_id: str, at: datetime, kind: str = "sitting", n: int = 1) -> None:
    # the figures read only who acted and when, so the rows name no problem,
    # question or item; the replica role skips the foreign keys
    with database.engine.begin() as conn:
        conn.execute(text("SET LOCAL session_replication_role = replica"))
        for i in range(n):
            key = f"{user_id}-{kind}-{at.isoformat()}-{i}"
            if kind == "sitting":
                conn.execute(
                    insert(sittings).values(id=key, user_id=user_id, problem_id=key, started_at=at)
                )
            elif kind == "attempt":
                conn.execute(
                    insert(attempts).values(
                        id=key, user_id=user_id, problem_id="p", finished_at=at, solved=True
                    )
                )
            elif kind == "answer":
                conn.execute(
                    insert(answers).values(
                        id=key,
                        client_id=key,
                        user_id=user_id,
                        device="d",
                        at=at,
                        created_at=NOW,
                        question_id="q",
                        correct=True,
                        guess=False,
                        missed=[],
                        traps=[],
                        wrong=False,
                    )
                )
            else:
                conn.execute(
                    insert(fills).values(
                        id=key, user_id=user_id, created_at=at, item_id="i", choice=0
                    )
                )


def test_an_empty_store_reads_thirty_days_of_zeros(database):
    """A day with no act still reads a row, so a gap reads as a gap."""
    read = product_figures(database, NOW, dev_user=None)

    assert (read.invited, read.signed_in, read.active) == (0, 0, 0)
    assert len(read.days) == 30
    assert read.days[0].day == date(2026, 11, 23) and read.days[-1].day == date(2026, 10, 25)
    assert all(one.learners == one.sittings == one.answers == 0 for one in read.days)
    assert [(one.counted, one.retained) for one in read.retention] == [(0, 0), (0, 0)]


def test_each_day_counts_its_acts_and_learners(database):
    named(database, LEARNER)
    named(database, OTHER)
    acted(database, LEARNER, NOW - timedelta(hours=1), "sitting")
    acted(database, LEARNER, NOW - timedelta(hours=1), "attempt", n=3)
    acted(database, OTHER, NOW - timedelta(hours=2), "answer", n=5)
    acted(database, OTHER, NOW - timedelta(days=1), "fill")

    read = product_figures(database, NOW, dev_user=None)

    today, yesterday = read.days[0], read.days[1]
    assert (today.learners, today.sittings, today.attempts, today.answers) == (2, 1, 3, 5)
    assert (yesterday.learners, yesterday.sittings, yesterday.answers) == (1, 0, 0)
    assert read.active == 2


def test_a_day_is_a_utc_day(database):
    """An act at 23:30 UTC counts on that UTC date."""
    named(database, LEARNER)
    acted(database, LEARNER, datetime(2026, 11, 22, 23, 30, tzinfo=UTC))

    read = product_figures(database, NOW, dev_user=None)

    assert read.days[1].day == date(2026, 11, 22) and read.days[1].sittings == 1


def test_an_answer_counts_on_the_day_the_client_gave_it(database):
    """`at`, not `created_at`: an answer synced days later keeps its own day."""
    named(database, LEARNER)
    acted(database, LEARNER, NOW - timedelta(days=3), "answer")

    read = product_figures(database, NOW, dev_user=None)

    assert read.days[3].answers == 1 and read.days[0].answers == 0


def test_retention_counts_only_users_old_enough(database):
    """A user first seen 3 days ago is in neither denominator."""
    named(database, LEARNER)
    named(database, OTHER)
    named(database, "u-c0e912")
    # back 10 days after a first act 40 days ago: retained at 7, and at 30 too
    acted(database, LEARNER, NOW - timedelta(days=40))
    acted(database, LEARNER, NOW - timedelta(days=1))
    # one act 20 days ago and none since: counted at 7, not retained
    acted(database, OTHER, NOW - timedelta(days=20))
    acted(database, "u-c0e912", NOW - timedelta(days=3))

    read = product_figures(database, NOW, dev_user=None)

    at_7, at_30 = read.retention
    assert (at_7.after_days, at_7.counted, at_7.retained) == (7, 2, 1)
    assert (at_30.after_days, at_30.counted, at_30.retained) == (30, 1, 1)


def test_the_author_is_left_out_of_every_figure(database):
    """The author's log, the eval set's, would read as the busiest learner."""
    invite(database, "author@example.com", Role.AUTHOR)
    invite(database, "learner@example.com", Role.LEARNER)
    author = signed_in(database, Provider.GOOGLE, "google-7", "author@example.com")
    learner = signed_in(database, Provider.GOOGLE, "google-8", "learner@example.com")
    named(database, "local")
    for user_id in (author, "local", learner):
        acted(database, user_id, NOW - timedelta(hours=1))

    read = product_figures(database, NOW, dev_user="local")

    assert (read.invited, read.signed_in, read.active) == (1, 1, 1)
    assert read.days[0].learners == 1 and read.days[0].sittings == 1


def test_the_route_returns_no_user_id(database):
    """The page counts across users and lists none."""
    named(database, LEARNER)
    acted(database, LEARNER, datetime.now(UTC) - timedelta(hours=1))
    client = authoring(database, "local")
    client.app.state.dev_user = "local"

    body = client.get("/api/author/product").text

    assert LEARNER not in body
    assert '"active":1' in body
