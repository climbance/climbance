"""diagnoses never name speed

Revision: b81a12e41432
Revises: 7427fc92bc00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "b81a12e41432"
down_revision: str | Sequence[str] | None = "7427fc92bc00"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Alembic compares no check constraint, so the change is written by hand
NAME = "diagnoses_never_speed_check"


def upgrade() -> None:
    op.create_check_constraint(op.f(NAME), "diagnoses", "mode <> 'speed'")


def downgrade() -> None:
    op.drop_constraint(op.f(NAME), "diagnoses", type_="check")
