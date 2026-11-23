import random
from datetime import UTC, datetime, timedelta

import pytest
from helpers import PROVENANCE, browsing, make_problem, stored_problem
from pydantic import ValidationError

from climb.cases import CaseLog
from climb.cold import COLD_LIMIT_SEC, eligible, read, serve_cold, submit_cold
from climb.log import AttemptLog, SittingStore
from climb.mint import case, sitting, user_rating
from climb.ratings import RatingLog
from climb.schema import CaseOutcome, Sitting
from climb.sitting import Refused, end, pause, submit

SERVED = datetime(2026, 11, 23, 10, tzinfo=UTC)
SOON = SERVED + timedelta(minutes=5)
PAST_LIMIT = SERVED + timedelta(seconds=COLD_LIMIT_SEC + 1)

USER = "u-4f9c2a"
DOUBLE = "def solve(n):\n    return n * 2\n"
WRONG = "def solve(n):\n    return n\n"


def rated(root, problem_id="p1", score=1500.0):
    stored_problem(root, problem_id, title="Sliding window maximum")
    CaseLog(root).append(case(problem_id, [0], 0, provenance=PROVENANCE))
    CaseLog(root).append(case(problem_id, [3], 6, provenance=PROVENANCE))
    RatingLog(root).append(user_rating(problem_id, score))


def served(root, at=SERVED):
    return serve_cold(root, user_id=USER, now=at, draw=random.Random(0))


def test_eligible_takes_scored_unseen_served_problems_alone():
    """A seen problem is not unseen, and an unscored one is no opponent."""
    problems = [make_problem(one) for one in ("p1", "p2", "p3", "p4")]
    retired = make_problem("p5", status="retired", retired_reason="defective")
    seen = [sitting(USER, "p2", SERVED)]

    found = eligible([*problems, retired], {"p1", "p2", "p4", "p5"}, seen, [])

    assert found == ["p1", "p4"]


def test_a_cold_sitting_reads_back_cold_with_its_limit_and_its_clock_running(database):
    """The flag and the limit are set at minting, the clock at serving."""
    rated(database)

    seated = served(database)

    stored = SittingStore(database).get(seated.sitting.id)
    assert stored is not None
    assert stored.cold and stored.time_limit_sec == COLD_LIMIT_SEC
    assert stored.clock_started_at == SERVED
    assert seated.elapsed_sec == 0


def test_the_reading_withholds_the_title_until_the_sitting_ends(database):
    """Some titles name the technique, and the difficulty is shown after."""
    rated(database, score=1700.0)
    seated = served(database)
    assert seated.revealed is None
    assert "title" not in seated.model_dump()

    end(SittingStore(database), seated.sitting.id, user_id=USER, now=SOON)
    after = read(database, seated.sitting.id, user_id=USER, now=SOON)

    assert after.revealed is not None
    assert after.revealed.title == "Sliding window maximum"
    assert after.revealed.score == 1700.0


def test_a_second_press_reaches_the_running_cold_sitting(database):
    """One runs at a time, so a second press is no second loss."""
    rated(database)
    rated(database, "p2")

    first = served(database)
    again = served(database, SOON)

    assert again.sitting.id == first.sitting.id


def test_a_cold_sitting_does_not_pause(database):
    """A contest's clock does not stop."""
    rated(database)
    seated = served(database)

    with pytest.raises(Refused, match="cold"):
        pause(SittingStore(database), seated.sitting.id, user_id=USER, now=SOON)


def test_a_submission_past_the_limit_is_refused_and_ends_the_sitting_at_the_limit(database):
    """The outcome is fixed at the limit, whenever a reader arrives."""
    rated(database)
    seated = served(database)
    for minutes in (40, 59):
        # the open page keeps the sitting touched, inside the idle bound
        read(database, seated.sitting.id, user_id=USER, now=SERVED + timedelta(minutes=minutes))

    with pytest.raises(Refused, match="time limit"):
        submit_cold(database, seated.sitting.id, DOUBLE, user_id=USER, now=PAST_LIMIT)

    stored = SittingStore(database).get(seated.sitting.id)
    assert stored is not None
    assert stored.ended_at == SERVED + timedelta(seconds=COLD_LIMIT_SEC)


def test_a_failing_cold_submission_names_the_case_by_number_alone(database):
    """A contest names the failing test and hides its input."""
    rated(database)
    seated = served(database)

    submitted = submit_cold(database, seated.sitting.id, WRONG, user_id=USER, now=SOON)

    assert submitted.failure is not None
    assert submitted.failure.model_dump() == {"number": 2, "outcome": CaseOutcome.WRONG}
    assert not submitted.attempt.solved


def test_a_reopened_cold_sitting_reads_its_last_verdict_by_number(database):
    """The reading carries no case input either."""
    rated(database)
    seated = served(database)
    submit_cold(database, seated.sitting.id, WRONG, user_id=USER, now=SOON)

    again = read(database, seated.sitting.id, user_id=USER, now=SOON)

    assert again.last is not None and again.last.failure is not None
    assert again.last.failure.number == 2


def test_the_drill_loops_submission_refuses_a_cold_sitting(database):
    """It would answer the failing case whole."""
    rated(database)
    seated = served(database)

    with pytest.raises(Refused, match="is cold"):
        submit(
            SittingStore(database),
            CaseLog(database),
            AttemptLog(database),
            seated.sitting.id,
            DOUBLE,
            user_id=USER,
            now=SOON,
        )


def test_no_eligible_problem_is_refused(database):
    """A problem with no score is no opponent."""
    stored_problem(database, "p1")

    with pytest.raises(Refused, match="no problem"):
        served(database)


def test_a_cold_sitting_without_its_limit_is_rejected():
    """A replay reads each sitting under the limit it ran under."""
    with pytest.raises(ValidationError, match="time limit"):
        Sitting(
            id="s1",
            user_id=USER,
            problem_id="p1",
            started_at=SERVED,
            clock_started_at=SERVED,
            cold=True,
        )


def test_a_limit_on_a_sitting_that_is_not_cold_is_rejected():
    """The limit is the cold sitting's alone."""
    with pytest.raises(ValidationError, match="cold sitting alone"):
        Sitting(id="s1", user_id=USER, problem_id="p1", started_at=SERVED, time_limit_sec=60)


def test_a_cold_sitting_served_through_the_api_reads_back_cold(database):
    """The page's route mints it, and a reload reads it without its title."""
    rated(database)
    client = browsing(database, USER)

    begun = client.post("/api/cold-sittings", json={}).json()
    again = client.get(f"/api/cold-sittings/{begun['sitting']['id']}").json()

    assert again["sitting"]["cold"] is True
    assert again["sitting"]["time_limit_sec"] == COLD_LIMIT_SEC
    assert "title" not in again and again["revealed"] is None
