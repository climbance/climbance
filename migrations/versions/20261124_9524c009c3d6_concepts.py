"""concepts

Revision: 9524c009c3d6
Revises: 3b8e5f1c07d2
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9524c009c3d6"
down_revision: str | Sequence[str] | None = "3b8e5f1c07d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "concepts",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("module_id", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("source", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.CheckConstraint("claim <> ''", name=op.f("concepts_claim_written_check")),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9][a-z0-9-]*$'", name=op.f("concepts_slug_spelled_check")
        ),
        sa.CheckConstraint("level BETWEEN 0 AND 3", name=op.f("concepts_level_in_range_check")),
        sa.ForeignKeyConstraint(
            ["module_id"], ["modules.id"], name=op.f("concepts_module_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("concepts_pkey")),
        sa.UniqueConstraint("module_id", "slug", name=op.f("concepts_module_id_slug_key")),
    )


def downgrade() -> None:
    op.drop_table("concepts")
