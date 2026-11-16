"""key_line_items, key_line_choices and fills

Revision: 642494a6b6ec
Revises: 8ddc6b2f200d
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "642494a6b6ec"
down_revision: str | Sequence[str] | None = "8ddc6b2f200d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# both types exist already: named rather than declared, so none is created
CASE_OUTCOME = postgresql.ENUM(name="case_outcome", create_type=False)
ITEM_STATUS = postgresql.ENUM(name="item_status", create_type=False)


def upgrade() -> None:
    op.create_table(
        "key_line_items",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("template_id", sa.Text(), nullable=False),
        sa.Column("form_digest", sa.Text(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("line", sa.Integer(), nullable=False),
        sa.Column("status", ITEM_STATUS, nullable=False),
        sa.CheckConstraint(
            "form_digest <> '' AND code <> ''", name=op.f("key_line_items_built_check")
        ),
        sa.CheckConstraint("line >= 1", name=op.f("key_line_items_line_counted_check")),
        sa.ForeignKeyConstraint(
            ["template_id"], ["card_templates.id"], name=op.f("key_line_items_template_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("key_line_items_pkey")),
    )
    op.create_index(
        op.f("key_line_items_template_id_idx"), "key_line_items", ["template_id"], unique=False
    )
    op.create_table(
        "fills",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("item_id", sa.Text(), nullable=False),
        sa.Column("choice", sa.Integer(), nullable=False),
        sa.CheckConstraint("choice >= 0", name=op.f("fills_choice_counted_check")),
        sa.ForeignKeyConstraint(
            ["item_id"], ["key_line_items.id"], name=op.f("fills_item_id_fkey")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fills_user_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("fills_pkey")),
        sa.UniqueConstraint("appended", name=op.f("fills_appended_key")),
    )
    op.create_index(op.f("fills_item_id_idx"), "fills", ["item_id"], unique=False)
    op.create_index(op.f("fills_user_id_idx"), "fills", ["user_id"], unique=False)
    op.create_table(
        "key_line_choices",
        sa.Column("item_id", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("change", sa.Text(), nullable=True),
        sa.Column(
            "case_args", postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), nullable=True
        ),
        sa.Column("case_expected", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("outcome", CASE_OUTCOME, nullable=True),
        sa.Column("returned", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint(
            "outcome IS NULL OR outcome <> 'timeout'",
            name=op.f("key_line_choices_no_timeout_check"),
        ),
        sa.CheckConstraint("text <> ''", name=op.f("key_line_choices_written_check")),
        sa.CheckConstraint(
            "correct = (change IS NULL AND case_args IS NULL AND outcome IS NULL)",
            name=op.f("key_line_choices_a_wrong_choice_names_its_case_check"),
        ),
        sa.ForeignKeyConstraint(
            ["item_id"], ["key_line_items.id"], name=op.f("key_line_choices_item_id_fkey")
        ),
        sa.PrimaryKeyConstraint("item_id", "position", name=op.f("key_line_choices_pkey")),
    )

    # by hand, since Alembic generates no trigger: `README.md`, Storage
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON fills"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_table("key_line_choices")
    op.drop_index(op.f("fills_user_id_idx"), table_name="fills")
    op.drop_index(op.f("fills_item_id_idx"), table_name="fills")
    op.drop_table("fills")
    op.drop_index(op.f("key_line_items_template_id_idx"), table_name="key_line_items")
    op.drop_table("key_line_items")
