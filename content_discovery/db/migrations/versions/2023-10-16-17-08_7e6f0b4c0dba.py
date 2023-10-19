"""Added likes table

Revision ID: 7e6f0b4c0dba
Revises: 075d6047b474
Create Date: 2023-10-16 17:08:33.320225

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7e6f0b4c0dba"
down_revision = "075d6047b474"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "likes",
        sa.Column("user_id", sa.String(), primary_key=True),
        sa.Column("snap_id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
            name=op.f("fk_likes_snaps_id"),
        ),
        sa.PrimaryKeyConstraint("user_id", "snap_id"),
    )


def downgrade() -> None:
    op.drop_table("likes")
