"""trace drills

Revision: b5e1c8d3a207
Revises: 9d3f6a2b8c41
"""

from collections.abc import Sequence

from alembic import op

revision: str = "b5e1c8d3a207"
down_revision: str | Sequence[str] | None = "9d3f6a2b8c41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE question_format ADD VALUE IF NOT EXISTS 'trace'")


def downgrade() -> None:
    pass  # Postgres drops no enum value, so `trace` stays
