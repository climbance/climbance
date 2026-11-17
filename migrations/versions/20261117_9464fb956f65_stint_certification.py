"""a certification exam's stint names the certification

Revision: 9464fb956f65
Revises: d10519bb7be1
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9464fb956f65"
down_revision: str | Sequence[str] | None = "d10519bb7be1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("stints", sa.Column("certification", sa.Text(), nullable=True))
    # by hand, since Alembic compares no check constraint
    op.create_check_constraint(
        op.f("stints_a_certification_names_an_exam_check"),
        "stints",
        "certification IS NULL OR (mode = 'exam' AND certification <> '')",
    )


def downgrade() -> None:
    op.drop_column("stints", "certification")
