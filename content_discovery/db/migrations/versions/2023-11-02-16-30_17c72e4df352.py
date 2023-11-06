"""empty message

Revision ID: 17c72e4df352
Revises: 5dc2a44b23db
Create Date: 2023-11-02 16:30:11.202519

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "17c72e4df352"
down_revision = "17c72e4df351"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE snaps SET visibility = 1")
    # ### end Alembic commands ###


def downgrade() -> None:
    pass


# ### end Alembic commands ###
