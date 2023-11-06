"""Added hashtags table

Revision ID: 844c236e9e58
Revises: 5dc2a44b23db
Create Date: 2023-11-01 22:44:28.102272

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "844c236e9e58"
down_revision = "5dc2a44b23db"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "hashtags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("snap_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
            name=op.f("fk_hashtag_snap_id"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("hashtags")
