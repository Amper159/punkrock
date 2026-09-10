"""add latitude/longitude to gig

Revision ID: c4a7f0e3b921
Revises: 9e19e201dbbd
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c4a7f0e3b921'
down_revision = '9e19e201dbbd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('gig', schema=None) as batch_op:
        batch_op.add_column(sa.Column('latitude', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('longitude', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('gig', schema=None) as batch_op:
        batch_op.drop_column('longitude')
        batch_op.drop_column('latitude')
