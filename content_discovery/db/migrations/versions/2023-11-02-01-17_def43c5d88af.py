"""Added mentions table

Revision ID: def43c5d88af
Revises: 844c236e9e58
Create Date: 2023-11-02 01:17:43.907540

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "def43c5d88af"
down_revision = "844c236e9e58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mentions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("mentioned_id", sa.String(), nullable=True),
        sa.Column("mentioned_username", sa.String(), nullable=True),
        sa.Column("snap_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
            name=op.f("fk_mention_snap_id"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("mentions")
