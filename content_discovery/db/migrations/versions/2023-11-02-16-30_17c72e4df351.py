"""Added visibility in snaps table

Revision ID: 17c72e4df351
Revises: def43c5d88af
Create Date: 2023-11-02 16:30:11.202519

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "17c72e4df351"
down_revision = "def43c5d88af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("snaps", sa.Column("visibility", sa.INTEGER(), default=1))
    op.execute("UPDATE snaps SET visibility = 1")


def downgrade() -> None:
    op.drop_column("snaps", "visibility")
