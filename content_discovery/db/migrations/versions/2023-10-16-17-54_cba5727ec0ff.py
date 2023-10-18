"""Added favorites table

Revision ID: cba5727ec0ff
Revises: c8a54f1ea7ad
Create Date: 2023-10-16 17:54:21.878833

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cba5727ec0ff"
down_revision = "c8a54f1ea7ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "favs",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("snap_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
            name=op.f("fk_favs_snaps_id"),
        ),
        sa.PrimaryKeyConstraint("user_id", "snap_id"),
    )


def downgrade() -> None:
    op.drop_table("favs")
