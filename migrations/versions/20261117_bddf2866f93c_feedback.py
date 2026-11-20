"""feedback

Revision: bddf2866f93c
Revises: e317a8ff4936
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "bddf2866f93c"
down_revision: str | Sequence[str] | None = "e317a8ff4936"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CLIENT = postgresql.ENUM("web", "native", name="client", create_type=False)


def upgrade() -> None:
    CLIENT.create(op.get_bind())
    op.create_table(
        "feedback",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("client", CLIENT, nullable=False),
        sa.Column("page", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "note ~ '\\S' AND length(note) <= 2000", name=op.f("feedback_note_written_check")
        ),
        sa.CheckConstraint(
            "length(page) BETWEEN 1 AND 200", name=op.f("feedback_page_named_check")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("feedback_user_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("feedback_pkey")),
        sa.UniqueConstraint("appended", name=op.f("feedback_appended_key")),
    )
    op.create_index(op.f("feedback_user_id_idx"), "feedback", ["user_id"], unique=False)

    # by hand, since Alembic generates no trigger: `database/README.md`
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON feedback"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_index(op.f("feedback_user_id_idx"), table_name="feedback")
    op.drop_table("feedback")
    CLIENT.drop(op.get_bind())
