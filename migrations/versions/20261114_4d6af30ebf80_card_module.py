"""card_module

Revision: 4d6af30ebf80
Revises: 6cc52f88d95b
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4d6af30ebf80"
down_revision: str | Sequence[str] | None = "6cc52f88d95b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # every card stored so far is an algorithms card
    op.add_column("cards", sa.Column("module", sa.Text(), server_default="algo", nullable=False))
    op.alter_column("cards", "module", server_default=None)


def downgrade() -> None:
    op.drop_column("cards", "module")
