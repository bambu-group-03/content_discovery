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
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("snap_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
            name=op.f("fk_likes_user_id_snaps"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("likes")
