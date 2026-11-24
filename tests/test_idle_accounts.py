from datetime import UTC, datetime, timedelta

from commands import connected, run_cli
from sqlalchemy import select, update

from climb.log import Provider, idle_accounts_deleted, idle_users, invite, opened, signed_in
from climb.log.table import app_tokens, sessions, users

NOW = datetime(2027, 12, 1, tzinfo=UTC)


def months_ago(months: int) -> datetime:
    return NOW - timedelta(days=round(months * 365 / 12))


def idle_since(database, email: str, months: int) -> str:
    """A user signed in once through a session last used `months` ago."""
    user_id = signed_in(database, Provider.GOOGLE, f"google-{email}", email)
    opened(database, user_id)
    with database.begin() as conn:
        conn.execute(update(users).where(users.c.id == user_id).values(created_at=months_ago(30)))
        conn.execute(
            update(sessions)
            .where(sessions.c.user_id == user_id)
            .values(created_at=months_ago(30), last_used_at=months_ago(months))
        )
    return user_id


def kept(database) -> set[str]:
    with database.connect() as conn:
        return set(conn.execute(select(users.c.id)).scalars())


def test_an_account_idle_a_year_goes_and_a_recent_or_invited_one_stays(database):
    """Twelve months idle deletes the account; eleven months, or an invitation
    on its email at thirteen, keeps it."""
    invite(database, "invited@example.com")
    gone = idle_since(database, "gone@example.com", 12)
    recent = idle_since(database, "recent@example.com", 11)
    invited = idle_since(database, "invited@example.com", 13)

    assert idle_accounts_deleted(database, NOW) == [gone]

    assert kept(database) == {recent, invited}


def test_an_app_token_in_use_keeps_an_account_whose_browser_is_idle(database):
    """The latest of every session and app token counts, not the first found."""
    user_id = idle_since(database, "phone@example.com", 20)
    with database.begin() as conn:
        conn.execute(
            app_tokens.insert().values(
                id="t-1",
                user_id=user_id,
                device="phone",
                created_at=months_ago(20),
                last_used_at=months_ago(1),
            )
        )

    assert idle_users(database, NOW) == []


def test_a_user_no_sign_in_names_counts_from_its_minting(database):
    user_id = signed_in(database, Provider.GITHUB, "github-3", "bare@example.com")

    now = datetime.now(UTC)
    assert idle_users(database, now + timedelta(days=364)) == []
    assert idle_users(database, now + timedelta(days=366)) == [user_id]


def test_the_terminal_prunes_without_a_confirmation(database, monkeypatch, capsys):
    """`climb log prune` runs from the server's timer, so it reads no stdin."""
    idle_since(database, "gone@example.com", 400)
    connected(database, monkeypatch)

    run_cli(monkeypatch, "log", "prune")

    assert "deleted 1 accounts" in capsys.readouterr().out
    assert kept(database) == set()
