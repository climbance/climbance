"""metric drills

Revision: 4e8b1d2c7a95
Revises: 7c2e4b9a1f03
"""

from collections.abc import Sequence

from alembic import op

revision: str = "4e8b1d2c7a95"
down_revision: str | Sequence[str] | None = "7c2e4b9a1f03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE question_format ADD VALUE IF NOT EXISTS 'metric'")


def downgrade() -> None:
    # Postgres drops no enum value, so `metric` stays
    pass
