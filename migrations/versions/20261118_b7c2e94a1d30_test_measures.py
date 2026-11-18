"""test measures

Revision: b7c2e94a1d30
Revises: e5a90c3d71b2
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7c2e94a1d30"
down_revision: str | Sequence[str] | None = "e5a90c3d71b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MEASURE = postgresql.ENUM("baseline", "delayed", name="measure", create_type=False)
LEVELLED = "(mode IN ('exam', 'baseline', 'delayed')) = (level IS NOT NULL)"
TOPICAL = "(mode IN ('baseline', 'delayed')) = (module_id IS NOT NULL AND topic_id IS NOT NULL)"


def upgrade() -> None:
    # a new enum value is usable once committed, and the checks below name it
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE stint_mode ADD VALUE IF NOT EXISTS 'baseline'")
        op.execute("ALTER TYPE stint_mode ADD VALUE IF NOT EXISTS 'delayed'")
    MEASURE.create(op.get_bind())
    op.add_column("answers", sa.Column("measure", MEASURE, nullable=True))
    op.add_column("stints", sa.Column("module_id", sa.Text(), nullable=True))
    op.add_column("stints", sa.Column("topic_id", sa.Text(), nullable=True))
    op.create_foreign_key(op.f("stints_module_id_fkey"), "stints", "modules", ["module_id"], ["id"])
    op.create_foreign_key(op.f("stints_topic_id_fkey"), "stints", "topics", ["topic_id"], ["id"])
    op.drop_constraint("an_exam_names_its_level", "stints", type_="check")
    op.create_check_constraint("an_exam_names_its_level", "stints", LEVELLED)
    op.create_check_constraint("a_test_names_its_topic", "stints", TOPICAL)


def downgrade() -> None:
    # Postgres drops no enum value, so the two added to stint_mode stay
    op.drop_constraint("a_test_names_its_topic", "stints", type_="check")
    op.drop_constraint("an_exam_names_its_level", "stints", type_="check")
    op.create_check_constraint(
        "an_exam_names_its_level", "stints", "(mode = 'exam') = (level IS NOT NULL)"
    )
    op.drop_constraint(op.f("stints_topic_id_fkey"), "stints", type_="foreignkey")
    op.drop_constraint(op.f("stints_module_id_fkey"), "stints", type_="foreignkey")
    op.drop_column("stints", "topic_id")
    op.drop_column("stints", "module_id")
    op.drop_column("answers", "measure")
    MEASURE.drop(op.get_bind())
