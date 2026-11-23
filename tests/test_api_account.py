from fastapi.testclient import TestClient
from helpers import browsing
from sqlalchemy import select

from climb.api import create_app
from climb.api.context import SESSION_COOKIE
from climb.api.signin import Client, SignIn
from climb.log import Provider, signed_in
from climb.log.table import sessions, users
from climb.storage import Database

USER = "u-4f9c2a"


def test_the_login_page_is_offered_every_configured_provider():
    """Read before anyone signs in, so the route needs no session."""
    clients = {
        Provider.GOOGLE: Client("google-id", "s"),
        Provider.GITHUB: Client("github-id", "s"),
    }
    app = create_app(Database(), sign_in=SignIn("http://localhost:5173", "a-key", clients))

    offered = TestClient(app).get("/api/sign-in").json()

    assert offered == {"providers": ["google", "github"], "dev_login": None}


def test_the_login_page_is_offered_the_dev_login_and_its_user():
    offered = TestClient(create_app(Database(), dev_login="local")).get("/api/sign-in").json()

    assert offered == {"providers": [], "dev_login": "local"}


def test_the_session_says_who_it_signs_in_as(database):
    """The menu names the user, and a dev login carries no address to name."""
    signed_in(database, Provider.GOOGLE, "google-7", "Solver@Example.com")
    user_id = signed_in(database, Provider.GOOGLE, "google-7", "solver@example.com")

    me = browsing(database, user_id).get("/api/me").json()

    assert me == {"user_id": user_id, "email": "solver@example.com", "author": False}


def test_a_user_no_provider_linked_carries_no_address(database):
    me = browsing(database, USER).get("/api/me").json()

    assert me == {"user_id": USER, "email": None, "author": False}


def test_who_the_session_signs_in_as_needs_a_session(database):
    assert TestClient(create_app(database)).get("/api/me").status_code == 401


def test_signing_out_revokes_the_session_and_clears_its_cookie(database):
    """Revoked on the server: a copy of the cookie kept elsewhere signs nobody
    in after the browser signed out."""
    client = browsing(database, USER)
    token = client.cookies[SESSION_COOKIE]

    response = client.delete("/api/session")

    assert response.status_code == 204
    assert 'session=""' in response.headers["set-cookie"]
    with database.connect() as conn:
        assert conn.execute(select(sessions.c.revoked_at)).scalar_one() is not None
    client.cookies.set(SESSION_COOKIE, token)
    assert client.get("/api/board").status_code == 401


def test_signing_out_without_a_session_still_answers(database):
    """A browser whose session already expired signs out as any other does."""
    client = TestClient(create_app(database), headers={"content-type": "application/json"})

    assert client.delete("/api/session").status_code == 204


def test_signing_out_is_a_write_another_site_cannot_forge(database):
    """A form posting to sign the user out is refused as any other write is."""
    client = browsing(database, USER)

    response = client.delete("/api/session", headers={"content-type": "text/plain"})

    assert response.status_code == 415
    assert client.get("/api/board").status_code == 200


def test_the_export_is_the_user_s_whole_log_as_a_file(database):
    response = browsing(database, USER).get("/api/account/export")

    assert response.json()["user_id"] == USER
    assert "attachment" in response.headers["content-disposition"]


def test_deleting_the_account_ends_its_session(database):
    """The user is gone, so the cookie it carried signs nobody in."""
    client = browsing(database, USER)

    response = client.request("DELETE", "/api/account", json={"confirm": USER})

    assert response.status_code == 204
    assert client.get("/api/me").status_code == 401
    with database.connect() as conn:
        assert conn.execute(select(users.c.id)).first() is None


def test_deleting_needs_the_account_s_email_typed_back(database):
    """The address the account menu names, since a mistyped press cannot be
    undone."""
    user_id = signed_in(database, Provider.GOOGLE, "google-7", "solver@example.com")
    client = browsing(database, user_id)

    refused = client.request("DELETE", "/api/account", json={"confirm": user_id})

    assert refused.status_code == 422
    assert client.get("/api/me").status_code == 200
    typed = client.request("DELETE", "/api/account", json={"confirm": "solver@example.com"})
    assert typed.status_code == 204
