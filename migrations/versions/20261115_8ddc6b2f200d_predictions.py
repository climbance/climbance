"""predictions

Revision: 8ddc6b2f200d
Revises: c44a58373e92
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8ddc6b2f200d"
down_revision: str | Sequence[str] | None = "c44a58373e92"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACT = postgresql.ENUM("recall", "sitting", "start", name="act")
ARM = postgresql.ENUM("scheduler", "baseline", name="arm")


def upgrade() -> None:
    ACT.create(op.get_bind())
    ARM.create(op.get_bind())
    op.create_table(
        "predictions",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("act", postgresql.ENUM(name="act", create_type=False), nullable=False),
        sa.Column("card_id", sa.Text(), nullable=False),
        sa.Column("template_id", sa.Text(), nullable=True),
        sa.Column("problem_id", sa.Text(), nullable=True),
        sa.Column("probe", sa.Boolean(), nullable=False),
        sa.Column("recall_probability", sa.Double(), nullable=True),
        sa.Column("fsrs_settings", sa.Text(), nullable=False),
        sa.Column("execution", sa.Double(), nullable=True),
        sa.Column("execution_settings", sa.Text(), nullable=False),
        sa.Column("arm", postgresql.ENUM(name="arm", create_type=False), nullable=True),
        sa.CheckConstraint(
            "execution BETWEEN 0 AND 1", name=op.f("predictions_execution_a_share_check")
        ),
        sa.CheckConstraint("rank BETWEEN 1 AND 5", name=op.f("predictions_rank_known_check")),
        sa.CheckConstraint(
            "recall_probability BETWEEN 0 AND 1",
            name=op.f("predictions_recall_probability_a_share_check"),
        ),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"], name=op.f("predictions_card_id_fkey")),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], name=op.f("predictions_problem_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["template_id"], ["card_templates.id"], name=op.f("predictions_template_id_fkey")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("predictions_user_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("predictions_pkey")),
        sa.UniqueConstraint("appended", name=op.f("predictions_appended_key")),
    )
    op.create_index(op.f("predictions_user_id_idx"), "predictions", ["user_id"], unique=False)

    # by hand, since Alembic generates no trigger: `README.md`, Storage
    op.execute(
        "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON predictions"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def downgrade() -> None:
    op.drop_index(op.f("predictions_user_id_idx"), table_name="predictions")
    op.drop_table("predictions")
    ARM.drop(op.get_bind())
    ACT.drop(op.get_bind())
