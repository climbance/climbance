from sqlalchemy import CheckConstraint, Column, Double, ForeignKey, Table, Text

from climb.schema import RatingSource
from climb.storage import appended_column, enumerated, metadata, timestamp

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
    # a key once the fits are stored: `corpus.md`, Difficulty fits
    Column("fit_id", Text),
    CheckConstraint(
        "(source = 'fit') = (fit_id IS NOT NULL) AND (source = 'fit') = (deviation IS NOT NULL)",
        name="fit_matches_source",
    ),
)
