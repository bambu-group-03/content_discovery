"""Added created_at in topics

Revision ID: 99db5c5d21ce
Revises: e09a79137b78
Create Date: 2023-12-07 02:01:14.219553

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "99db5c5d21ce"
down_revision = "e09a79137b78"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("topics", sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("topics", "created_at")
