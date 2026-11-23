"""The emails allowed to sign in, matched lowercased as an identity's are, and
the role each one lets its user reach."""

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert

from climb.log.table import Role, identities, invitations
from climb.storage import Database


def invite(root: Database, email: str, role: Role = Role.LEARNER) -> None:
    """Lets the email sign in with the role. Inviting it again sets the role."""
    statement = insert(invitations).values(email=email.lower(), created_at=func.now(), role=role)
    with root.begin() as conn:
        conn.execute(
            statement.on_conflict_do_update(
                index_elements=[invitations.c.email], set_={"role": statement.excluded.role}
            )
        )


def withdraw(root: Database, email: str) -> bool:
    """Stops the email signing in again. `False` where it was never invited."""
    with root.begin() as conn:
        removed = conn.execute(delete(invitations).where(invitations.c.email == email.lower()))
    return removed.rowcount > 0


def invited(root: Database, email: str) -> bool:
    query = select(invitations.c.email).where(invitations.c.email == email.lower())
    with root.connect() as conn:
        return conn.execute(query).first() is not None


def invitations_held(root: Database) -> list[tuple[str, Role]]:
    query = select(invitations.c.email, invitations.c.role).order_by(invitations.c.email)
    with root.connect() as conn:
        return [(email, role) for email, role in conn.execute(query)]


def authored(root: Database, user_id: str) -> bool:
    """Whether an email of the user's identities holds an author invitation."""
    query = (
        select(identities.c.user_id)
        .join(invitations, invitations.c.email == identities.c.email)
        .where(identities.c.user_id == user_id, invitations.c.role == Role.AUTHOR)
        .limit(1)
    )
    with root.connect() as conn:
        return conn.execute(query).first() is not None
