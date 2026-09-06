"""add half day absent statuses

Revision ID: 6eea5e16b785
Revises: 001_initial_tables
Create Date: 2026-08-28 03:29:51.174577

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6eea5e16b785'
down_revision: Union[str, Sequence[str], None] = '001_initial_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use execute since we cannot use transactional DDL for ALTER TYPE ADD VALUE in Postgres
    op.execute("ALTER TYPE attendance_status ADD VALUE 'absent_half_morning'")
    op.execute("ALTER TYPE attendance_status ADD VALUE 'absent_half_afternoon'")


def downgrade() -> None:
    pass
