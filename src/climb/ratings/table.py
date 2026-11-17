from sqlalchemy import CheckConstraint, Column, Double, ForeignKey, Integer, Table, Text

from climb.schema import RatingSource
from climb.storage import appended_column, enumerated, metadata, timestamp

difficulty_fits = Table(
    "difficulty_fits",
    metadata,
    Column("id", Text, primary_key=True),
    appended_column(),
    Column("created_at", timestamp(), nullable=False),
    Column("anchor_set", Text, nullable=False),
    Column("slope", Double, nullable=False),
    Column("intercept", Double, nullable=False),
    Column("anchors_fitted", Integer, nullable=False),
    Column("anchors_held_out", Integer, nullable=False),
    Column("problems", Integer, nullable=False),
    Column("held_out_log_loss", Double, nullable=False),
    Column("baseline_log_loss", Double, nullable=False),
    CheckConstraint("slope > 0", name="harder_scores_higher"),
)

# one row per member, in the panel's order, weak to strong
difficulty_fit_members = Table(
    "difficulty_fit_members",
    metadata,
    Column("fit_id", Text, ForeignKey("difficulty_fits.id"), primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("model", Text, nullable=False),
    Column("effort", Text, nullable=False),
    Column("pin", Text, nullable=False),
    Column("ability", Double, nullable=False),
    Column("trials", Integer, nullable=False),
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
    Column("fit_id", Text, ForeignKey("difficulty_fits.id")),
    CheckConstraint(
        "(source = 'fit') = (fit_id IS NOT NULL) AND (source = 'fit') = (deviation IS NOT NULL)",
        name="fit_matches_source",
    ),
)
