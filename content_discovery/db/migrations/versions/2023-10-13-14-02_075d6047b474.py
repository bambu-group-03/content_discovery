"""empty message

Revision ID: 075d6047b474
Revises: 8f0e5e709e3a
Create Date: 2023-10-13 14:02:51.808542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '075d6047b474'
down_revision = '8f0e5e709e3a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('snaps',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=280), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('dummy_model', 'name',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('dummy_model', 'name',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
    op.drop_table('snaps')
    # ### end Alembic commands ###
