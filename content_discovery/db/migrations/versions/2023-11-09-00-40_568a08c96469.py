"""fix

Revision ID: 568a08c96469
Revises: 78d16c6b80c5
Create Date: 2023-11-09 00:40:00.261823

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "568a08c96469"
down_revision = "78d16c6b80c5"
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
