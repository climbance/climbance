"""call users

Revision: 5d1c7e2a9b40
Revises: 9524c009c3d6
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5d1c7e2a9b40"
down_revision: str | Sequence[str] | None = "9524c009c3d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("calls", sa.Column("user_id", sa.Text(), nullable=True))
    op.create_foreign_key(op.f("calls_user_id_fkey"), "calls", "users", ["user_id"], ["id"])
    op.create_index(op.f("calls_user_id_created_at_idx"), "calls", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index(op.f("calls_user_id_created_at_idx"), table_name="calls")
    op.drop_constraint(op.f("calls_user_id_fkey"), "calls", type_="foreignkey")
    op.drop_column("calls", "user_id")
