"""Running one CLI command in a test, as a shell would."""

from climb import cli
from climb.cli import transport as TRANSPORT


def run_cli(monkeypatch, *argv: str, client=None) -> None:
    """`climb <argv>` through `main`. With `client`, the transport is the
    fake and a key is set, since a command checks for one before it asks."""
    if client is not None:
        faked(monkeypatch, client)
    monkeypatch.setattr("sys.argv", ["climb", *argv])
    cli.main()


def faked(monkeypatch, client) -> None:
    """Every transport a command builds answers from `client`: the router,
    and the subscription CLIs at a version of their own."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setattr(TRANSPORT, "OpenRouter", lambda _api, **_: client)
    monkeypatch.setattr(TRANSPORT, "Subscription", lambda **_: client)
    monkeypatch.setattr(TRANSPORT, "version", lambda name: f"{name} 1.0.0")


def connected(database, monkeypatch):
    """Points the command under test at the test's database, the one
    DATABASE_URL names, and returns the handle the test seeds it through."""
    url = database.engine.url.render_as_string(hide_password=False)
    monkeypatch.setenv("DATABASE_URL", url)
    return database
