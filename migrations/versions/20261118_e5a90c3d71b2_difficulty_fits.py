"""difficulty fits

Revision: e5a90c3d71b2
Revises: 9464fb956f65
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5a90c3d71b2"
down_revision: str | Sequence[str] | None = "9464fb956f65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "difficulty_fits",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("anchor_set", sa.Text(), nullable=False),
        sa.Column("slope", sa.Double(), nullable=False),
        sa.Column("intercept", sa.Double(), nullable=False),
        sa.Column("anchors_fitted", sa.Integer(), nullable=False),
        sa.Column("anchors_held_out", sa.Integer(), nullable=False),
        sa.Column("problems", sa.Integer(), nullable=False),
        sa.Column("held_out_log_loss", sa.Double(), nullable=False),
        sa.Column("baseline_log_loss", sa.Double(), nullable=False),
        sa.CheckConstraint("slope > 0", name=op.f("difficulty_fits_harder_scores_higher_check")),
        sa.PrimaryKeyConstraint("id", name=op.f("difficulty_fits_pkey")),
        sa.UniqueConstraint("appended", name=op.f("difficulty_fits_appended_key")),
    )
    op.create_table(
        "difficulty_fit_members",
        sa.Column("fit_id", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("effort", sa.Text(), nullable=False),
        sa.Column("pin", sa.Text(), nullable=False),
        sa.Column("ability", sa.Double(), nullable=False),
        sa.Column("trials", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fit_id"], ["difficulty_fits.id"], name=op.f("difficulty_fit_members_fit_id_fkey")
        ),
        sa.PrimaryKeyConstraint("fit_id", "position", name=op.f("difficulty_fit_members_pkey")),
    )
    op.create_foreign_key(
        op.f("difficulty_ratings_fit_id_fkey"),
        "difficulty_ratings",
        "difficulty_fits",
        ["fit_id"],
        ["id"],
    )
    # by hand, since Alembic generates no trigger: `database/README.md`
    for table in ("difficulty_fits", "difficulty_fit_members"):
        op.execute(
            f"CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON {table}"
            " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
        )


def downgrade() -> None:
    op.drop_constraint(
        op.f("difficulty_ratings_fit_id_fkey"), "difficulty_ratings", type_="foreignkey"
    )
    op.drop_table("difficulty_fit_members")
    op.drop_table("difficulty_fits")
