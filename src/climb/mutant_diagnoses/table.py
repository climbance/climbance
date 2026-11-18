from sqlalchemy import Column, ForeignKey, Table, Text

from climb.schema import Cause
from climb.storage import appended_column, call_column, enumerated, metadata, timestamp

mutant_diagnoses = Table(
    "mutant_diagnoses",
    metadata,
    Column("id", Text, primary_key=True),
    appended_column(),
    Column("created_at", timestamp(), nullable=False),
    Column("template_id", Text, ForeignKey("card_templates.id"), nullable=False),
    Column("form_digest", Text, nullable=False),
    Column("code_hash", Text, nullable=False),
    Column("cause", enumerated(Cause), nullable=False),
    Column("evidence", Text, nullable=False),
    call_column(nullable=False),
)
