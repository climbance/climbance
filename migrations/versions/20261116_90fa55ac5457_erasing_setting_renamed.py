"""erasing setting renamed

Revision: 90fa55ac5457
Revises: 45b1261b968d
"""

from collections.abc import Sequence

from alembic import op

revision: str = "90fa55ac5457"
down_revision: str | Sequence[str] | None = "45b1261b968d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # the rename edited d60b4e1b2049 in place, so a database migrated before
    # it reads the setting under the engine's old name and refuses an erasure
    op.execute(
        """
        CREATE OR REPLACE FUNCTION refuse_rewrite() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' AND current_setting('climb.erasing', true) = 'on' THEN
                RETURN NULL;
            END IF;
            RAISE EXCEPTION '% is append-only: % refused', TG_TABLE_NAME, TG_OP;
        END
        $$
        """
    )


def downgrade() -> None:
    # d60b4e1b2049 as it now reads defines the same function
    pass
