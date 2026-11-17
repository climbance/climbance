"""statement_written refuses a blank statement

Revision: 7427fc92bc00
Revises: 783504c53d6f
"""

from collections.abc import Sequence

from alembic import op

revision: str = "7427fc92bc00"
down_revision: str | Sequence[str] | None = "783504c53d6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Alembic compares no check constraint, so the change is written by hand
NAME = "problems_statement_written_check"


def upgrade() -> None:
    op.drop_constraint(op.f(NAME), "problems", type_="check")
    op.create_check_constraint(op.f(NAME), "problems", "statement ~ '\\S'")


def downgrade() -> None:
    op.drop_constraint(op.f(NAME), "problems", type_="check")
    op.create_check_constraint(op.f(NAME), "problems", "statement <> ''")
