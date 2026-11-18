"""diagnosis_cause

Revision: 2a3ee8c55ce4
Revises: b7c2e94a1d30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2a3ee8c55ce4"
down_revision: str | Sequence[str] | None = "b7c2e94a1d30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# no diagnosis is stored anywhere, so the column is replaced rather than mapped
CAUSE = postgresql.ENUM("slip", "form", name="cause", create_type=False)
FAILURE_MODE = postgresql.ENUM(
    "speed", "rust", "gap", "syntax", "none", name="failure_mode", create_type=False
)
NEVER_SPEED = "diagnoses_never_speed_check"


def upgrade() -> None:
    CAUSE.create(op.get_bind())
    op.add_column("diagnoses", sa.Column("cause", CAUSE, nullable=False))
    # the never-speed check goes with the column it reads
    op.drop_column("diagnoses", "mode")


def downgrade() -> None:
    op.add_column("diagnoses", sa.Column("mode", FAILURE_MODE, nullable=False))
    op.create_check_constraint(op.f(NEVER_SPEED), "diagnoses", "mode <> 'speed'")
    op.drop_column("diagnoses", "cause")
    CAUSE.drop(op.get_bind())
