"""add comment and gig_photo tables

Revision ID: 3f8b1d6a4c02
Revises: c4a7f0e3b921
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '3f8b1d6a4c02'
down_revision = 'c4a7f0e3b921'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=20), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('author_name', sa.String(length=80), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_target_type'), ['target_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_comment_target_id'), ['target_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comment_is_approved'), ['is_approved'], unique=False)
        batch_op.create_index(batch_op.f('ix_comment_created_at'), ['created_at'], unique=False)

    op.create_table(
        'gig_photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('gig_id', sa.Integer(), nullable=True),
        sa.Column('uploader_name', sa.String(length=80), nullable=False),
        sa.Column('caption', sa.String(length=200), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['gig_id'], ['gig.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('gig_photo', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_gig_photo_gig_id'), ['gig_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_gig_photo_is_approved'), ['is_approved'], unique=False)
        batch_op.create_index(batch_op.f('ix_gig_photo_created_at'), ['created_at'], unique=False)


def downgrade():
    op.drop_table('gig_photo')
    op.drop_table('comment')
