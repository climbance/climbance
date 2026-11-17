"""a problem names exactly one target

Revision: d10519bb7be1
Revises: b81a12e41432
"""

from collections.abc import Sequence

from alembic import op

revision: str = "d10519bb7be1"
down_revision: str | Sequence[str] | None = "b81a12e41432"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Alembic compares no check constraint, so the change is written by hand
NAME = "problems_one_target_check"


def upgrade() -> None:
    op.drop_constraint(op.f(NAME), "problems", type_="check")
    op.create_check_constraint(
        op.f(NAME), "problems", "(target_template_id IS NULL) <> (target_technique IS NULL)"
    )


def downgrade() -> None:
    op.drop_constraint(op.f(NAME), "problems", type_="check")
    op.create_check_constraint(
        op.f(NAME), "problems", "target_template_id IS NULL OR target_technique IS NULL"
    )
