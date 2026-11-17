import json
import logging

import pytest
from fastapi.testclient import TestClient
from helpers import browsing

from climb.api.app import create_app
from climb.api.feedback import ERRORS_PER_MINUTE, _reported
from climb.caps import RUNS_PER_MINUTE
from climb.cli.feedback import feedback_listed
from climb.log import FeedbackLog, account_deleted, erased, whole_log
from climb.schema import Client

USER = "u-4f9c2a"
NOTE = "The timer kept running after I paused it on the phone."
REPORT = {
    "client": "web",
    "version": "0.1.0",
    "page": "/problems/p1",
    "message": "Cannot read properties of undefined",
    "stack": "at SittingView (SittingView.tsx:12)",
}


@pytest.fixture
def client(database):
    _reported.clear()
    return browsing(database, USER)


def sending(client, **body):
    return client.post(
        "/api/feedback", json={"client": "native", "page": "/settings", "note": NOTE} | body
    )


def test_feedback_is_stored_with_where_it_was_sent_from(client, database):
    """The page names what the remark is about, and the two clients' paths
    differ."""
    assert sending(client).status_code == 201

    (stored,) = FeedbackLog(database).all()
    assert (stored.user_id, stored.client, stored.page, stored.note) == (
        USER,
        Client.NATIVE,
        "/settings",
        NOTE,
    )


def test_feedback_needs_a_note(client):
    """A blank note passes a presence check while saying nothing."""
    assert sending(client, note=" \n").status_code == 422


def test_feedback_is_capped_like_a_run(client, database):
    """Each note is a row the author reads, so one user's burst is capped."""
    for _ in range(RUNS_PER_MINUTE):
        assert sending(client).status_code == 201

    assert sending(client).status_code == 429
    assert len(FeedbackLog(database).all()) == RUNS_PER_MINUTE


def test_feedback_is_exported_and_erased_with_the_log(client, database):
    """Feedback is the user's own record, private as the rest of the log."""
    sending(client)

    assert [one.note for one in whole_log(database, USER).feedback] == [NOTE]
    assert erased(database, USER)["feedback"] == 1
    assert FeedbackLog(database).all() == []


def test_deleting_the_account_deletes_its_feedback(client, database):
    sending(client)

    account_deleted(database, USER)

    assert FeedbackLog(database).all() == []


def test_an_error_report_is_one_line_in_the_api_s_log(client, caplog):
    """The report is kept as long as the log, 14 days, and names the user so
    the author can ask what they did."""
    with caplog.at_level(logging.WARNING, logger="climb.api.feedback"):
        assert client.post("/api/errors", json=REPORT).status_code == 204

    (line,) = [one.getMessage() for one in caplog.records]
    assert json.loads(line.removeprefix("client error: ")) == {"user_id": USER, **REPORT}


def test_error_reports_are_capped_per_minute(client):
    """A client failing in a loop would otherwise fill the log."""
    for _ in range(ERRORS_PER_MINUTE):
        assert client.post("/api/errors", json=REPORT).status_code == 204

    assert client.post("/api/errors", json=REPORT).status_code == 429


def test_an_error_report_needs_a_session(database):
    """Only a signed-in user writes to the log, as only one runs code."""
    anonymous = TestClient(create_app(database), headers={"content-type": "application/json"})

    assert anonymous.post("/api/errors", json=REPORT).status_code == 401


def test_the_author_lists_feedback_newest_first(client, database, capsys):
    """The author reads feedback in the terminal, as the retirement requests."""
    sending(client, note="first")
    sending(client, note="second")

    feedback_listed(database)

    lines = capsys.readouterr().out.splitlines()
    assert [line.split(": ", 1)[-1] for line in lines[:2]] == ["second", "first"]
    assert f"{USER}  native /settings" in lines[0]
    assert lines[-1] == "2 notes of feedback"
