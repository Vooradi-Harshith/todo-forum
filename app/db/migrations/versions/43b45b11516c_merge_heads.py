"""merge heads

Revision ID: 43b45b11516c
Revises: 2728d6425fa2, eb2bf8469b09
Create Date: 2025-12-01 11:17:04.052009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43b45b11516c'
down_revision: Union[str, Sequence[str], None] = ('2728d6425fa2', 'eb2bf8469b09')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
