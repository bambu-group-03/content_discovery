"""Added parent_id in snaps table

Revision ID: 5dc2a44b23db
Revises: ad2315fb468b
Create Date: 2023-11-01 14:27:25.524714

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5dc2a44b23db"
down_revision = "ad2315fb468b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "snaps",
        sa.Column("parent_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_snap_parent_id",
        "snaps",
        "snaps",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_column("snaps", "parent_id")
