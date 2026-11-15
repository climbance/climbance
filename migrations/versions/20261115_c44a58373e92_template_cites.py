"""template_cites

Revision: c44a58373e92
Revises: 4d6af30ebf80
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c44a58373e92"
down_revision: str | Sequence[str] | None = "4d6af30ebf80"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "card_templates",
        sa.Column(
            "cites", postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("card_templates", "cites")
