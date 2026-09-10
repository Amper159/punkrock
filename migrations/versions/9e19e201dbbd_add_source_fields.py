"""add source/link-out fields to gig and article

Revision ID: 9e19e201dbbd
Revises: 823ccd35e717
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e19e201dbbd'
down_revision = '823ccd35e717'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('gig', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('external_id', sa.String(length=120), nullable=True))
        batch_op.create_index(batch_op.f('ix_gig_external_id'), ['external_id'], unique=True)

    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('source_name', sa.String(length=120), nullable=True))


def downgrade():
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_column('source_name')
        batch_op.drop_column('source_url')

    with op.batch_alter_table('gig', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_gig_external_id'))
        batch_op.drop_column('external_id')
        batch_op.drop_column('source')
