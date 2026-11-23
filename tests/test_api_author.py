import pytest
from fastapi.testclient import TestClient
from helpers import browsing
from test_seed_knowledge import authored, with_concepts

from climb.api import create_app
from climb.knowledge import read_module, seed_module
from climb.log import Provider, Role, invite, signed_in, withdraw
from climb.storage import Database

USER = "u-4f9c2a"


def every_call() -> list[tuple[str, str]]:
    # the schema lists every route included in it, and an author route is never
    # left out of it. A path parameter is filled with a value no record holds,
    # since the guard answers first
    paths = create_app(Database()).openapi()["paths"]
    return [
        (method.upper(), path.replace("{", "").replace("}", ""))
        for path, operations in paths.items()
        if path.startswith("/api/author")
        for method in operations
    ]


def test_the_author_area_has_a_route_to_guard():
    """The walk below would pass on an empty list."""
    assert ("GET", "/api/author") in every_call()


@pytest.mark.parametrize(("method", "path"), every_call())
def test_a_learner_reaches_no_author_route(database, method, path):
    """Every route under `/api/author/`, those added later included."""
    learner = browsing(database, USER)

    assert learner.request(method, path).status_code == 403


@pytest.mark.parametrize(("method", "path"), every_call())
def test_no_author_route_answers_without_a_session(database, method, path):
    assert TestClient(create_app(database)).request(method, path).status_code == 401


def test_an_author_invitation_opens_the_author_area(database):
    invite(database, "author@example.com", Role.AUTHOR)
    user_id = signed_in(database, Provider.GOOGLE, "google-7", "author@example.com")
    author = browsing(database, user_id)

    assert author.get("/api/author").status_code == 200
    assert author.get("/api/me").json()["author"]


def test_a_withdrawn_invitation_closes_the_author_area_at_once(database):
    """The role is read from the invitation at each request."""
    invite(database, "author@example.com", Role.AUTHOR)
    user_id = signed_in(database, Provider.GOOGLE, "google-7", "author@example.com")
    author = browsing(database, user_id)

    withdraw(database, "author@example.com")

    assert author.get("/api/author").status_code == 403


def test_the_dev_login_is_the_author(database):
    """The local engine shows its own pages with no invitation to set."""
    client = browsing(database, "local")
    client.app.state.dev_user = "local"

    assert client.get("/api/author").status_code == 200
    assert client.get("/api/me").json()["author"]


def test_the_generation_page_reads_an_empty_store(database):
    """Every figure answers on a store no run has written to."""
    client = browsing(database, "local")
    client.app.state.dev_user = "local"

    read = client.get("/api/author/generation").json()

    assert (read["writings"], read["landed"], read["spend_per_landed"]) == (0, 0, None)
    assert read["stops"] == [] and read["drafts"] == []


def test_the_concepts_route_reads_one_module_s_concepts(database, tmp_path):
    """The hosted engine holds no `content/` to read a concept from."""
    base = with_concepts(authored(tmp_path), "list-mutable")
    seed_module(read_module(base), root=database)
    client = browsing(database, "local")
    client.app.state.dev_user = "local"

    read = client.get("/api/author/concepts", params={"module": "python"}).json()

    assert [c["claim"] for c in read["concepts"]] == ["A list is mutated through its references."]
    assert client.get("/api/author/concepts", params={"module": "algo"}).json()["concepts"] == []
