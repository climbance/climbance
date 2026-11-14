"""subtopic_techniques

Revision: 6cc52f88d95b
Revises: a36fc93426bc
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6cc52f88d95b"
down_revision: str | Sequence[str] | None = "a36fc93426bc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "subtopics",
        sa.Column(
            "techniques",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("subtopics", "techniques")
