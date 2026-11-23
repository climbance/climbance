"""cold sittings

Revision: a9ef1eba70cc
Revises: 4162a18a6a2b
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a9ef1eba70cc"
down_revision: str | Sequence[str] | None = "4162a18a6a2b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Alembic compares no check constraint, so those are written by hand
CHECKS = {
    "sittings_limit_on_cold_check": "cold = (time_limit_sec IS NOT NULL)",
    "sittings_limit_positive_check": "time_limit_sec > 0",
}


def upgrade() -> None:
    op.add_column(
        "sittings", sa.Column("cold", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )
    op.add_column("sittings", sa.Column("time_limit_sec", sa.Integer(), nullable=True))
    for name, condition in CHECKS.items():
        op.create_check_constraint(op.f(name), "sittings", condition)


def downgrade() -> None:
    for name in CHECKS:
        op.drop_constraint(op.f(name), "sittings", type_="check")
    op.drop_column("sittings", "time_limit_sec")
    op.drop_column("sittings", "cold")
