"""fix

Revision ID: 78d16c6b80c5
Revises: 17c72e4df352
Create Date: 2023-11-09 00:28:50.799141

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "78d16c6b80c5"
down_revision = "17c72e4df352"
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
