from sqlalchemy import CheckConstraint, Column, Double, ForeignKey, Integer, Table, Text

from climb.schema import RatingSource
from climb.storage import appended_column, call_column, enumerated, metadata, timestamp

difficulty_corrections = Table(
    "difficulty_corrections",
    metadata,
    Column("id", Text, primary_key=True),
    appended_column(),
    Column("created_at", timestamp(), nullable=False),
    Column("anchor_set", Text, nullable=False),
    Column("model", Text, nullable=False),
    Column("effort", Text, nullable=False),
    Column("pin", Text, nullable=False),
    Column("temperature", Double),
    Column("instructions_hash", Text, nullable=False),
    Column("draws", Integer, nullable=False),
    Column("intercept", Double, nullable=False),
    Column("slope", Double, nullable=False),
    Column("anchors_fitted", Integer, nullable=False),
    Column("anchors_held_out", Integer, nullable=False),
    Column("held_out_spearman", Double, nullable=False),
    Column("held_out_mean_error", Double, nullable=False),
    Column("deviation", Double, nullable=False),
    CheckConstraint("slope > 0", name="harder_scores_higher"),
)

# an anchor's draws are never stored here: `cli/difficulty/judge.md`
difficulty_draws = Table(
    "difficulty_draws",
    metadata,
    Column("id", Text, primary_key=True),
    appended_column(),
    Column("created_at", timestamp(), nullable=False),
    Column("problem_id", Text, ForeignKey("problems.id"), nullable=False, index=True),
    Column("judged", Integer, nullable=False),
    call_column(nullable=False),
)

difficulty_ratings = Table(
    "difficulty_ratings",
    metadata,
    Column("id", Text, primary_key=True),
    appended_column(),
    Column("created_at", timestamp(), nullable=False),
    Column("problem_id", Text, ForeignKey("problems.id"), nullable=False, index=True),
    Column("score", Double, nullable=False),
    Column("deviation", Double),
    Column("source", enumerated(RatingSource), nullable=False),
    Column("correction_id", Text, ForeignKey("difficulty_corrections.id")),
    CheckConstraint(
        "(source = 'judge') = (correction_id IS NOT NULL)"
        " AND (source = 'judge') = (deviation IS NOT NULL)",
        name="judge_matches_source",
    ),
)

# one row per draw a judge rating's median read, in the order it read them
difficulty_rating_draws = Table(
    "difficulty_rating_draws",
    metadata,
    Column("rating_id", Text, ForeignKey("difficulty_ratings.id"), primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("draw_id", Text, ForeignKey("difficulty_draws.id"), nullable=False),
)
