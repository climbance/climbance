"""estimate drills

Revision: 7c2e4b9a1f03
Revises: 3a8f1c6d2e57
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7c2e4b9a1f03"
down_revision: str | Sequence[str] | None = "3a8f1c6d2e57"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE question_format ADD VALUE IF NOT EXISTS 'estimate'")
    op.add_column("answers", sa.Column("estimate", sa.Double(), nullable=True))
    op.create_check_constraint(
        "an_open_question_takes_no_estimate", "answers", "grade IS NULL OR estimate IS NULL"
    )


def downgrade() -> None:
    # Postgres drops no enum value, so `estimate` stays
    op.drop_constraint("an_open_question_takes_no_estimate", "answers", type_="check")
    op.drop_column("answers", "estimate")
