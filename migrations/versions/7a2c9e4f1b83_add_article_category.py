"""add category to article

Revision ID: 7a2c9e4f1b83
Revises: 3f8b1d6a4c02
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '7a2c9e4f1b83'
down_revision = '3f8b1d6a4c02'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=20), nullable=True, server_default='novinka'))
        batch_op.create_index(batch_op.f('ix_article_category'), ['category'], unique=False)


def downgrade():
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_article_category'))
        batch_op.drop_column('category')
