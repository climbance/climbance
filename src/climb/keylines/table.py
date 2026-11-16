from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Table, Text
from sqlalchemy.dialects.postgresql import JSONB

from climb.schema import CaseOutcome, ItemStatus
from climb.storage import enumerated, metadata, timestamp

# created once, and only the status moves: `README.md`, Data classes
key_line_items = Table(
    "key_line_items",
    metadata,
    Column("id", Text, primary_key=True),
    Column("created_at", timestamp(), nullable=False),
    Column("template_id", Text, ForeignKey("card_templates.id"), nullable=False, index=True),
    Column("form_digest", Text, nullable=False),
    Column("code", Text, nullable=False),
    Column("line", Integer, nullable=False),
    Column("status", enumerated(ItemStatus), nullable=False),
    CheckConstraint("form_digest <> '' AND code <> ''", name="built"),
    CheckConstraint("line >= 1", name="line_counted"),
)

# one row per choice, in the order a fill names it by
key_line_choices = Table(
    "key_line_choices",
    metadata,
    Column("item_id", Text, ForeignKey("key_line_items.id"), primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("text", Text, nullable=False),
    Column("correct", Boolean, nullable=False),
    Column("change", Text),
    # JSON of any shape by design, as a case's are. A `None` stores as JSON null
    Column("case_args", JSONB(none_as_null=True)),
    Column("case_expected", JSONB(none_as_null=False), nullable=False),
    Column("outcome", enumerated(CaseOutcome)),
    Column("returned", JSONB(none_as_null=False), nullable=False),
    CheckConstraint("text <> ''", name="written"),
    CheckConstraint(
        "correct = (change IS NULL AND case_args IS NULL AND outcome IS NULL)",
        name="a_wrong_choice_names_its_case",
    ),
    CheckConstraint("outcome IS NULL OR outcome <> 'timeout'", name="no_timeout"),
)
