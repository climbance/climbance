"""judge drills

Revision: 9d3f6a2b8c41
Revises: 4e8b1d2c7a95
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9d3f6a2b8c41"
down_revision: str | Sequence[str] | None = "4e8b1d2c7a95"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE question_format ADD VALUE IF NOT EXISTS 'judge'")
    op.add_column("answers", sa.Column("called_clean", sa.Boolean(), nullable=True))
    op.add_column("answers", sa.Column("tapped", sa.Integer(), nullable=True))
    op.add_column("answers", sa.Column("located", sa.Boolean(), nullable=True))
    op.create_check_constraint(
        "a_clean_call_taps_no_line", "answers", "NOT called_clean OR tapped IS NULL"
    )


def downgrade() -> None:
    # Postgres drops no enum value, so `judge` stays
    op.drop_constraint("a_clean_call_taps_no_line", "answers", type_="check")
    op.drop_column("answers", "located")
    op.drop_column("answers", "tapped")
    op.drop_column("answers", "called_clean")
