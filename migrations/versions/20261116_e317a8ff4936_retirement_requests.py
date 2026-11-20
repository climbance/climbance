"""retirement requests

Revision: e317a8ff4936
Revises: c41f8d2a7e93
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e317a8ff4936"
down_revision: str | Sequence[str] | None = "c41f8d2a7e93"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RETIREMENT_REASON = postgresql.ENUM(
    "defective", "copied", name="retirement_reason", create_type=False
)


def upgrade() -> None:
    op.create_table(
        "retirement_requests",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("problem_id", sa.Text(), nullable=False),
        sa.Column("reason", RETIREMENT_REASON, nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "note ~ '\\S' AND length(note) <= 2000",
            name=op.f("retirement_requests_note_written_check"),
        ),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], name=op.f("retirement_requests_problem_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("retirement_requests_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("retirement_requests_pkey")),
        sa.UniqueConstraint("appended", name=op.f("retirement_requests_appended_key")),
    )
    op.create_index(
        op.f("retirement_requests_problem_id_idx"),
        "retirement_requests",
        ["problem_id"],
        unique=False,
    )
    op.create_index(
        op.f("retirement_requests_user_id_idx"), "retirement_requests", ["user_id"], unique=False
    )

    # by hand, since Alembic generates no trigger: `database/README.md`
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON retirement_requests"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_index(op.f("retirement_requests_user_id_idx"), table_name="retirement_requests")
    op.drop_index(op.f("retirement_requests_problem_id_idx"), table_name="retirement_requests")
    op.drop_table("retirement_requests")
