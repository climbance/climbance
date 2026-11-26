"""placement

Revision: 3a8f1c6d2e57
Revises: 5d1c7e2a9b40
"""

from collections.abc import Sequence

from alembic import op

revision: str = "3a8f1c6d2e57"
down_revision: str | Sequence[str] | None = "5d1c7e2a9b40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TOPICAL = (
    "(mode IN ('baseline', 'delayed', 'placement'))"
    " = (module_id IS NOT NULL AND topic_id IS NOT NULL)"
)
TESTED = "(mode IN ('baseline', 'delayed')) = (module_id IS NOT NULL AND topic_id IS NOT NULL)"


def upgrade() -> None:
    # a new enum value is usable once committed, and the check below names it
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE stint_mode ADD VALUE IF NOT EXISTS 'placement'")
        op.execute("ALTER TYPE measure ADD VALUE IF NOT EXISTS 'placement'")
    op.drop_constraint("a_test_names_its_topic", "stints", type_="check")
    op.create_check_constraint("a_test_names_its_topic", "stints", TOPICAL)


def downgrade() -> None:
    # Postgres drops no enum value, so the two added stay
    op.drop_constraint("a_test_names_its_topic", "stints", type_="check")
    op.create_check_constraint("a_test_names_its_topic", "stints", TESTED)
