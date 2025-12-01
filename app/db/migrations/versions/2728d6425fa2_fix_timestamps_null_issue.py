"""fix timestamps null issue

Revision ID: 2728d6425fa2
Revises: 70019c1e91bb
Create Date: 2025-11-28 11:14:12.748663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2728d6425fa2'
down_revision: Union[str, Sequence[str], None] = '70019c1e91bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


def upgrade():
    # POSTS
    op.alter_column("posts", "created_at",
        server_default=sa.text("NOW()"), existing_nullable=False)
    op.alter_column("posts", "updated_at",
        server_default=sa.text("NOW()"), existing_nullable=False)

    # COMMENTS
    op.alter_column("comments", "created_at",
        server_default=sa.text("NOW()"), existing_nullable=False)
    op.alter_column("comments", "updated_at",
        server_default=sa.text("NOW()"), existing_nullable=False)

    # NOTIFICATIONS
    op.alter_column("notifications", "created_at",
        server_default=sa.text("NOW()"), existing_nullable=False)
    op.alter_column("notifications", "updated_at",
        server_default=sa.text("NOW()"), existing_nullable=False)

def downgrade():
    pass



def downgrade() -> None:
    """Downgrade schema."""
    pass
