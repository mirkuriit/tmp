"""add_event_moderation_decision_id

Revision ID: 7c1d9e4b5a20
Revises: aec24262bcd0
Create Date: 2026-10-30 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7c1d9e4b5a20'
down_revision: str | Sequence[str] | None = 'aec24262bcd0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('events', sa.Column('moderation_decision_id', sa.Uuid(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('events', 'moderation_decision_id')
