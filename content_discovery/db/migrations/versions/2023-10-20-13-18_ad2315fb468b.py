"""Added likes, shares and favs to snaps table

Revision ID: ad2315fb468b
Revises: cba5727ec0ff
Create Date: 2023-10-20 13:18:08.534178

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ad2315fb468b"
down_revision = "cba5727ec0ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("snaps", sa.Column("likes", sa.INTEGER, default=0))
    op.add_column("snaps", sa.Column("shares", sa.INTEGER, default=0))
    op.add_column("snaps", sa.Column("favs", sa.INTEGER, default=0))

    op.execute("UPDATE snaps SET likes = 0, shares = 0, favs = 0")


def downgrade() -> None:
    op.drop_column("snaps", "likes")
    op.drop_column("snaps", "shares")
    op.drop_column("snaps", "favs")
