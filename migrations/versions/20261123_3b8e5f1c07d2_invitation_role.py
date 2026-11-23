"""invitation role

Revision: 3b8e5f1c07d2
Revises: a9ef1eba70cc
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "3b8e5f1c07d2"
down_revision: str | Sequence[str] | None = "a9ef1eba70cc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLE = postgresql.ENUM("learner", "author", name="role", create_type=False)


def upgrade() -> None:
    ROLE.create(op.get_bind())
    op.add_column(
        "invitations",
        sa.Column("role", ROLE, server_default="learner", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("invitations", "role")
    ROLE.drop(op.get_bind())
