"""empty message

Revision ID: e09a79137b78
Revises: 4a1f97e3b9fb
Create Date: 2023-11-25 19:18:20.225469

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e09a79137b78"
down_revision = "4a1f97e3b9fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "relationships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("snap_id", sa.Uuid(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["snap_id"],
            ["snaps.id"],
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint("fk_snap_parent_id", "snaps", type_="foreignkey")
    op.create_foreign_key(None, "snaps", "snaps", ["parent_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(
        "fk_snap_parent_id",
        "snaps",
        "snaps",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_table("relationships")
    op.drop_table("topics")
    # ### end Alembic commands ###
