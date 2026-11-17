"""run_faults

Revision: 783504c53d6f
Revises: bddf2866f93c
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "783504c53d6f"
down_revision: str | Sequence[str] | None = "bddf2866f93c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RUN_KIND = postgresql.ENUM("submission", "recall", name="run_kind", create_type=False)


def upgrade() -> None:
    RUN_KIND.create(op.get_bind())
    op.create_table(
        "run_faults",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("kind", RUN_KIND, nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.CheckConstraint("length(detail) <= 2000", name=op.f("run_faults_detail_bounded_check")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("run_faults_user_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("run_faults_pkey")),
        sa.UniqueConstraint("appended", name=op.f("run_faults_appended_key")),
    )
    op.create_index(op.f("run_faults_user_id_idx"), "run_faults", ["user_id"], unique=False)

    # by hand, since Alembic generates no trigger: `README.md`, Storage
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON run_faults"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_index(op.f("run_faults_user_id_idx"), table_name="run_faults")
    op.drop_table("run_faults")
    RUN_KIND.drop(op.get_bind())
