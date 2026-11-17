import pytest
from helpers import browsing, seed_problem

from climb.log import RetirementRequestLog, account_deleted, erased, whole_log
from climb.problems import ProblemStore
from climb.schema import RetirementReason

USER = "u-4f9c2a"
NOTE = "The cases expect the indices sorted, and the statement never says so."


@pytest.fixture
def client(database):
    seed_problem(database, id="p1", techniques=["sorting"])
    return browsing(database, USER)


def requesting(client, problem_id="p1", **body):
    return client.post(
        f"/api/problems/{problem_id}/retirement-requests",
        json={"reason": "defective", "note": NOTE} | body,
    )


def test_a_request_is_stored_and_the_problem_stays_served(client, database):
    """The author retires the problem by hand. No user retires a problem every
    user is served."""
    response = requesting(client)

    assert response.status_code == 201
    (stored,) = RetirementRequestLog(database).for_problem("p1")
    assert (stored.user_id, stored.reason, stored.note) == (USER, RetirementReason.DEFECTIVE, NOTE)
    assert ProblemStore(database).get("p1").served


def test_a_request_needs_a_note(client):
    """The author reads the note to judge the problem, so a blank one says
    nothing to judge."""
    assert requesting(client, note="  \n ").status_code == 422


def test_a_retired_problem_takes_no_request(client, database):
    ProblemStore(database).retire("p1", RetirementReason.DEFECTIVE)

    assert requesting(client).status_code == 409


def test_an_unknown_problem_takes_no_request(client):
    assert requesting(client, problem_id="p-none").status_code == 404


def test_a_request_is_exported_and_erased_with_the_log(client, database):
    """A request is the user's own record, private as the rest of the log."""
    requesting(client)

    assert [one.note for one in whole_log(database, USER).retirement_requests] == [NOTE]
    assert erased(database, USER)["retirement_requests"] == 1
    assert RetirementRequestLog(database).all() == []


def test_deleting_the_account_deletes_its_requests(client, database):
    requesting(client)

    account_deleted(database, USER)

    assert RetirementRequestLog(database).all() == []
