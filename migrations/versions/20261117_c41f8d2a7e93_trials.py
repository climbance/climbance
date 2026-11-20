"""trials

Revision: c41f8d2a7e93
Revises: b7d2e19c4a60
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c41f8d2a7e93"
down_revision: str | Sequence[str] | None = "b7d2e19c4a60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# case_outcome exists already: named rather than declared, so none is created
CASE_OUTCOME = postgresql.ENUM(
    "passed", "wrong", "timeout", "crashed", name="case_outcome", create_type=False
)


def upgrade() -> None:
    op.create_table(
        "trials",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("problem_id", sa.Text(), nullable=False),
        sa.Column("try_number", sa.Integer(), nullable=False),
        sa.Column("outcome", CASE_OUTCOME, nullable=True),
        sa.Column("cases_passed", sa.Integer(), nullable=False),
        sa.Column("cases_run", sa.Integer(), nullable=False),
        sa.Column("cap_ms", sa.Integer(), nullable=False),
        sa.Column("runner", sa.Text(), nullable=False),
        sa.Column("call_id", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "cases_passed <= cases_run", name=op.f("trials_passed_within_run_check")
        ),
        sa.CheckConstraint(
            "(outcome IS NULL) = (cases_run = 0)", name=op.f("trials_outcome_iff_run_check")
        ),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], name=op.f("trials_call_id_fkey")),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], name=op.f("trials_problem_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("trials_pkey")),
        sa.UniqueConstraint("appended", name=op.f("trials_appended_key")),
    )
    op.create_index(op.f("trials_problem_id_idx"), "trials", ["problem_id"])
    # by hand, since Alembic generates no trigger: `database/README.md`
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON trials"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_index(op.f("trials_problem_id_idx"), table_name="trials")
    op.drop_table("trials")
