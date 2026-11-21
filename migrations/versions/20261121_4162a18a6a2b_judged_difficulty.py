"""judged difficulty

Revision: 4162a18a6a2b
Revises: 6088483e28d5
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4162a18a6a2b"
down_revision: str | Sequence[str] | None = "6088483e28d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

JUDGE_CHECK = (
    "(source = 'judge') = (correction_id IS NOT NULL)"
    " AND (source = 'judge') = (deviation IS NOT NULL)"
)
FIT_CHECK = "(source = 'fit') = (fit_id IS NOT NULL) AND (source = 'fit') = (deviation IS NOT NULL)"


def append_only(table: str) -> None:
    # by hand, since Alembic generates no trigger: `database/README.md`
    op.execute(
        f"CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON {table}"
        " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
    )


def source_type(*values: str) -> None:
    # Postgres drops no enum value, so the type is written again
    op.execute("ALTER TYPE rating_source RENAME TO rating_source_old")
    op.execute(f"CREATE TYPE rating_source AS ENUM ({', '.join(f"'{v}'" for v in values)})")
    op.execute(
        "ALTER TABLE difficulty_ratings ALTER COLUMN source TYPE rating_source"
        " USING source::text::rating_source"
    )
    op.execute("DROP TYPE rating_source_old")


def upgrade() -> None:
    op.create_table(
        "difficulty_corrections",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("anchor_set", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("effort", sa.Text(), nullable=False),
        sa.Column("pin", sa.Text(), nullable=False),
        sa.Column("temperature", sa.Double(), nullable=True),
        sa.Column("instructions_hash", sa.Text(), nullable=False),
        sa.Column("draws", sa.Integer(), nullable=False),
        sa.Column("intercept", sa.Double(), nullable=False),
        sa.Column("slope", sa.Double(), nullable=False),
        sa.Column("anchors_fitted", sa.Integer(), nullable=False),
        sa.Column("anchors_held_out", sa.Integer(), nullable=False),
        sa.Column("held_out_spearman", sa.Double(), nullable=False),
        sa.Column("held_out_mean_error", sa.Double(), nullable=False),
        sa.Column("deviation", sa.Double(), nullable=False),
        sa.CheckConstraint(
            "slope > 0", name=op.f("difficulty_corrections_harder_scores_higher_check")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("difficulty_corrections_pkey")),
        sa.UniqueConstraint("appended", name=op.f("difficulty_corrections_appended_key")),
    )
    op.create_table(
        "difficulty_draws",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("problem_id", sa.Text(), nullable=False),
        sa.Column("judged", sa.Integer(), nullable=False),
        sa.Column("call_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["call_id"], ["calls.id"], name=op.f("difficulty_draws_call_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], name=op.f("difficulty_draws_problem_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("difficulty_draws_pkey")),
        sa.UniqueConstraint("appended", name=op.f("difficulty_draws_appended_key")),
    )
    op.create_index(op.f("difficulty_draws_problem_id_idx"), "difficulty_draws", ["problem_id"])
    op.create_table(
        "difficulty_rating_draws",
        sa.Column("rating_id", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("draw_id", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["draw_id"], ["difficulty_draws.id"], name=op.f("difficulty_rating_draws_draw_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["rating_id"],
            ["difficulty_ratings.id"],
            name=op.f("difficulty_rating_draws_rating_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("rating_id", "position", name=op.f("difficulty_rating_draws_pkey")),
    )
    for table in ("difficulty_corrections", "difficulty_draws", "difficulty_rating_draws"):
        append_only(table)

    # no fit was ever stored, so no rating names one: `cli/difficulty/fits.md`
    op.drop_constraint(
        op.f("difficulty_ratings_fit_matches_source_check"), "difficulty_ratings", type_="check"
    )
    op.drop_constraint(
        op.f("difficulty_ratings_fit_id_fkey"), "difficulty_ratings", type_="foreignkey"
    )
    op.drop_column("difficulty_ratings", "fit_id")
    op.drop_table("difficulty_fit_members")
    op.drop_table("difficulty_fits")
    source_type("user", "judge")
    op.add_column("difficulty_ratings", sa.Column("correction_id", sa.Text(), nullable=True))
    op.create_foreign_key(
        op.f("difficulty_ratings_correction_id_fkey"),
        "difficulty_ratings",
        "difficulty_corrections",
        ["correction_id"],
        ["id"],
    )
    op.create_check_constraint(
        op.f("difficulty_ratings_judge_matches_source_check"), "difficulty_ratings", JUDGE_CHECK
    )


def downgrade() -> None:
    # a judge rating has no shape before this revision: none is dropped silently
    judged = op.get_bind().execute(
        sa.text("SELECT count(*) FROM difficulty_ratings WHERE source = 'judge'")
    )
    if judged.scalar_one():
        raise RuntimeError("judge ratings are stored; this revision cannot be undone")
    op.drop_constraint(
        op.f("difficulty_ratings_judge_matches_source_check"), "difficulty_ratings", type_="check"
    )
    op.drop_constraint(
        op.f("difficulty_ratings_correction_id_fkey"), "difficulty_ratings", type_="foreignkey"
    )
    op.drop_column("difficulty_ratings", "correction_id")
    source_type("user", "fit")
    op.drop_table("difficulty_rating_draws")
    op.drop_table("difficulty_draws")
    op.drop_table("difficulty_corrections")
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
    for table in ("difficulty_fits", "difficulty_fit_members"):
        append_only(table)
    op.add_column("difficulty_ratings", sa.Column("fit_id", sa.Text(), nullable=True))
    op.create_foreign_key(
        op.f("difficulty_ratings_fit_id_fkey"),
        "difficulty_ratings",
        "difficulty_fits",
        ["fit_id"],
        ["id"],
    )
    op.create_check_constraint(
        op.f("difficulty_ratings_fit_matches_source_check"), "difficulty_ratings", FIT_CHECK
    )
