"""add_memo_to_scheduletype

Revision ID: bff8ada92eb4
Revises: c41980276beb
Create Date: 2026-03-08 18:05:57.559023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bff8ada92eb4'
down_revision: Union[str, Sequence[str], None] = 'c41980276beb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE scheduletype ADD VALUE 'MEMO'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
