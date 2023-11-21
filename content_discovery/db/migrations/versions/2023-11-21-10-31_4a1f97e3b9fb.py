"""empty message

Revision ID: 4a1f97e3b9fb
Revises: 17c72e4df351
Create Date: 2023-11-21 10:31:53.996762

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4a1f97e3b9fb"
down_revision = "17c72e4df351"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("snaps", sa.Column("privacy", sa.Integer(), default=1))
    op.execute("UPDATE snaps SET privacy = 1")


def downgrade() -> None:
    op.drop_column("snaps", "privacy")
