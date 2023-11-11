"""Added shares table

Revision ID: c8a54f1ea7ad
Revises: 7e6f0b4c0dba
Create Date: 2023-10-16 17:49:27.569445

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c8a54f1ea7ad"
down_revision = "7e6f0b4c0dba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shares",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("snap_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
            name=op.f("fk_shares_snaps_id"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("shares")
