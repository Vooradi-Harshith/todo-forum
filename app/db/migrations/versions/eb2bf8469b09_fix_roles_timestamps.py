from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# 🔥 ADD THESE
revision = 'eb2bf8469b09'   # your file name prefix
down_revision = '048c8a06d93d'  # previous migration id
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "roles", "created_at",
        server_default=sa.text("NOW()"),
        existing_type=sa.TIMESTAMP(timezone=True)
    )
    op.alter_column(
        "roles", "updated_at",
        server_default=sa.text("NOW()"),
        existing_type=sa.TIMESTAMP(timezone=True)
    )


def downgrade():
    op.alter_column("roles", "created_at", server_default=None)
    op.alter_column("roles", "updated_at", server_default=None)


def upgrade():
    op.alter_column("roles", "created_at",
        server_default=sa.text("NOW()"), existing_type=sa.TIMESTAMP(timezone=True))

    op.alter_column("roles", "updated_at",
        server_default=sa.text("NOW()"), existing_type=sa.TIMESTAMP(timezone=True))


def downgrade():
    op.alter_column("roles", "created_at", server_default=None)
    op.alter_column("roles", "updated_at", server_default=None)
