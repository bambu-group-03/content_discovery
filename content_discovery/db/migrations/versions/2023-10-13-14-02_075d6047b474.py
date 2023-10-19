"""Added snaps table

Revision ID: 075d6047b474
Revises: 2b7380507a71
Create Date: 2023-10-13 14:02:51.808542

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "075d6047b474"
down_revision = "2b7380507a71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "snaps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("content", sa.String(length=280), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("snaps")
