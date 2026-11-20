"""difficulty scores

Revision: b7d2e19c4a60
Revises: 90fa55ac5457
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7d2e19c4a60"
down_revision: str | Sequence[str] | None = "90fa55ac5457"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RATING_SOURCE = postgresql.ENUM("user", "fit", name="rating_source", create_type=False)
PROBLEM_DIFFICULTY = postgresql.ENUM(
    "easy", "medium", "hard", name="problem_difficulty", create_type=False
)
CLAIM_SOURCE = postgresql.ENUM("user", "classifier", name="claim_source", create_type=False)

TRIGGER = (
    "CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON difficulty_ratings"
    " FOR EACH STATEMENT EXECUTE FUNCTION refuse_rewrite()"
)


def upgrade() -> None:
    # a label rating carries no score, and `cli/difficulty/README.md` deletes it
    # rather than keep a second shape: the table is written again, empty
    op.drop_table("difficulty_ratings")
    RATING_SOURCE.create(op.get_bind())
    op.create_table(
        "difficulty_ratings",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("problem_id", sa.Text(), nullable=False),
        sa.Column("score", sa.Double(), nullable=False),
        sa.Column("deviation", sa.Double(), nullable=True),
        sa.Column("source", RATING_SOURCE, nullable=False),
        sa.Column("fit_id", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(source = 'fit') = (fit_id IS NOT NULL)"
            " AND (source = 'fit') = (deviation IS NOT NULL)",
            name=op.f("difficulty_ratings_fit_matches_source_check"),
        ),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], name=op.f("difficulty_ratings_problem_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("difficulty_ratings_pkey")),
        sa.UniqueConstraint("appended", name=op.f("difficulty_ratings_appended_key")),
    )
    op.create_index(op.f("difficulty_ratings_problem_id_idx"), "difficulty_ratings", ["problem_id"])
    # by hand, since Alembic generates no trigger: `database/README.md`
    op.execute(TRIGGER)


def downgrade() -> None:
    op.drop_table("difficulty_ratings")
    RATING_SOURCE.drop(op.get_bind())
    op.create_table(
        "difficulty_ratings",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("appended", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("problem_id", sa.Text(), nullable=False),
        sa.Column("difficulty", PROBLEM_DIFFICULTY, nullable=False),
        sa.Column("source", CLAIM_SOURCE, nullable=False),
        sa.Column("call_id", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(source = 'classifier') = (call_id IS NOT NULL)",
            name=op.f("difficulty_ratings_call_matches_source_check"),
        ),
        sa.ForeignKeyConstraint(
            ["call_id"], ["calls.id"], name=op.f("difficulty_ratings_call_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], name=op.f("difficulty_ratings_problem_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("difficulty_ratings_pkey")),
        sa.UniqueConstraint("appended", name=op.f("difficulty_ratings_appended_key")),
    )
    op.create_index(op.f("difficulty_ratings_problem_id_idx"), "difficulty_ratings", ["problem_id"])
    op.execute(TRIGGER)
