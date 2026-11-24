"""The accounts nobody signed in to for a year, deleted as the account menu
deletes one: `api/sign-in.md`."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import exists, func, select, union_all

from climb.log.owned import account_deleted
from climb.log.table import app_tokens, identities, invitations, sessions, users
from climb.storage import Database

IDLE = timedelta(days=365)


def idle_users(root: Database, now: datetime | None = None) -> list[str]:
    """Each user whose sessions and app tokens last signed a request in a year
    ago or more, and none of whose identities' emails holds an invitation."""
    cutoff = (now or datetime.now(UTC)) - IDLE
    used = union_all(
        select(sessions.c.user_id, sessions.c.last_used_at.label("at")),
        select(app_tokens.c.user_id, app_tokens.c.last_used_at.label("at")),
        # a user no sign-in row names counts from its minting
        select(users.c.id.label("user_id"), users.c.created_at.label("at")),
    ).subquery()
    invited = exists().where(
        identities.c.user_id == used.c.user_id, identities.c.email == invitations.c.email
    )
    query = (
        select(used.c.user_id)
        .where(~invited)
        .group_by(used.c.user_id)
        .having(func.max(used.c.at) <= cutoff)
        .order_by(used.c.user_id)
    )
    with root.connect() as conn:
        return list(conn.execute(query).scalars())


def idle_accounts_deleted(root: Database, now: datetime | None = None) -> list[str]:
    """Deletes each idle user's account, one transaction each, and returns
    their ids."""
    found = idle_users(root, now)
    for user_id in found:
        account_deleted(root, user_id)
    return found
