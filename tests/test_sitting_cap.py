from datetime import UTC, datetime, timedelta

import pytest
from helpers import PROVENANCE, stored_problem

from climb.caps import RUNS_PER_HOUR, RUNS_PER_MINUTE, TooOften
from climb.cases import CaseLog
from climb.log import AttemptLog, Faulted, RunFaultLog, SittingStore
from climb.mint import case
from climb.runner import RunnerError
from climb.schema import RunKind, Sitting
from climb.sitting import submit

STARTED = datetime(2026, 9, 10, 8, tzinfo=UTC)
TEN = datetime(2026, 9, 10, 10, tzinfo=UTC)

# a wrong answer, and the cap is counted on one sitting
TRIPLE = "def solve(n):\n    return n * 3\n"


class Stores:
    """Two sittings on one problem, each a different user's."""

    def __init__(self, root) -> None:
        self.sittings = SittingStore(root)
        self.cases = CaseLog(root)
        self.log = AttemptLog(root)
        stored_problem(root, "p1")
        for sitting_id, user_id in (("s1", "u-4f9c2a"), ("s2", "u-77b3e1")):
            self.sittings.put(
                Sitting.model_validate(
                    {
                        "id": sitting_id,
                        "user_id": user_id,
                        "problem_id": "p1",
                        "started_at": STARTED,
                        "clock_started_at": STARTED,
                        # touched where the submissions land, since the bound
                        # would otherwise end a sitting left since STARTED
                        "last_active_at": TEN,
                    }
                )
            )
        self.cases.append(case("p1", [1], 2, provenance=PROVENANCE))

    def submit(self, *, at: datetime = TEN, sitting_id: str = "s1", user_id: str = "u-4f9c2a"):
        return submit(
            self.sittings, self.cases, self.log, sitting_id, TRIPLE, user_id=user_id, now=at
        )

    def fill(self, **whose: str) -> None:
        for _ in range(RUNS_PER_MINUTE):
            self.submit(**whose)


def test_a_submission_past_the_cap_is_refused(database):
    """Each submission runs untrusted code on the server, and the broker admits
    one run at a time, so one user's burst is every other user's wait."""
    stores = Stores(database)
    stores.fill()

    with pytest.raises(TooOften, match="cap"):
        stores.submit()


def test_a_refused_submission_mints_no_attempt(database):
    """The cap is refused before the run, so the log carries what ran and
    nothing else."""
    stores = Stores(database)
    stores.fill()

    with pytest.raises(TooOften):
        stores.submit()

    assert len(stores.log.attempts("u-4f9c2a")) == RUNS_PER_MINUTE


def test_the_cap_is_a_rate_rather_than_a_total(database):
    """The same submission stands a minute later, since the count reads the
    minute before it."""
    stores = Stores(database)
    stores.fill()

    later = stores.submit(at=TEN + timedelta(minutes=1, seconds=1))

    assert later.verification.results


def test_the_cap_counts_one_user_s_own_submissions(database):
    """A reader given a user reads that user's records, so one user's burst is
    not another user's refusal."""
    stores = Stores(database)
    stores.fill()

    theirs = stores.submit(sitting_id="s2", user_id="u-77b3e1")

    assert theirs.verification.results


def test_the_hour_caps_what_the_minute_lets_through(database):
    """Ten a minute is 600 an hour, so the hour holds a user's queue to a share
    the other users can wait out."""
    stores = Stores(database)
    # six a minute, under the minute's cap throughout
    for n in range(RUNS_PER_HOUR):
        stores.submit(at=TEN + timedelta(seconds=10 * n))

    with pytest.raises(TooOften, match="an hour"):
        stores.submit(at=TEN + timedelta(seconds=10 * RUNS_PER_HOUR))


def broken(*_args, **_kwargs):
    raise RunnerError("the run's container exited 137 after 0 of 1 cases")


def test_a_faulted_submission_is_stored_and_counted(database, monkeypatch):
    """A solution can end its own sandbox, so a run answering no result still
    holds the broker, and a fault loop meets the cap as any burst does."""
    stores = Stores(database)
    monkeypatch.setattr("climb.sitting.judge", broken)
    for _ in range(RUNS_PER_MINUTE):
        with pytest.raises(Faulted):
            stores.submit()
    monkeypatch.undo()

    with pytest.raises(TooOften):
        stores.submit()

    faults = RunFaultLog(database).for_user("u-4f9c2a")
    assert [one.kind for one in faults] == [RunKind.SUBMISSION] * RUNS_PER_MINUTE
    assert stores.log.attempts("u-4f9c2a") == []
