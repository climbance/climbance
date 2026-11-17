from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Table, Text

from climb.schema import CaseOutcome
from climb.storage import appended_column, call_column, enumerated, metadata, timestamp

# an anchor's trials are never stored here: `corpus.md`, Trials
trials = Table(
    "trials",
    metadata,
    Column("id", Text, primary_key=True),
    appended_column(),
    Column("created_at", timestamp(), nullable=False),
    Column("problem_id", Text, ForeignKey("problems.id"), nullable=False, index=True),
    Column("try_number", Integer, nullable=False),
    Column("outcome", enumerated(CaseOutcome)),
    Column("cases_passed", Integer, nullable=False),
    Column("cases_run", Integer, nullable=False),
    Column("cap_ms", Integer, nullable=False),
    Column("runner", Text, nullable=False),
    call_column(nullable=False),
    CheckConstraint("cases_passed <= cases_run", name="passed_within_run"),
    CheckConstraint("(outcome IS NULL) = (cases_run = 0)", name="outcome_iff_run"),
)
