"""mutant_diagnoses

Revision: 6088483e28d5
Revises: 2a3ee8c55ce4
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6088483e28d5"
down_revision: str | Sequence[str] | None = "2a3ee8c55ce4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# cause exists already: named rather than declared, so none is created
CAUSE = postgresql.ENUM("slip", "form", name="cause", create_type=False)


def upgrade() -> None:
    op.create_table(
        "mutant_diagnoses",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("template_id", sa.Text(), nullable=False),
        sa.Column("form_digest", sa.Text(), nullable=False),
        sa.Column("code_hash", sa.Text(), nullable=False),
        sa.Column("cause", CAUSE, nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("call_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["call_id"], ["calls.id"], name=op.f("mutant_diagnoses_call_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["template_id"], ["card_templates.id"], name=op.f("mutant_diagnoses_template_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("mutant_diagnoses_pkey")),
        sa.UniqueConstraint("appended", name=op.f("mutant_diagnoses_appended_key")),
    )
    # by hand, since Alembic generates no trigger: `README.md`, Storage
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON mutant_diagnoses"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_table("mutant_diagnoses")
