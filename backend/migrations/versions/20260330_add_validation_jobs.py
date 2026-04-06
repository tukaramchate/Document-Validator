"""
Revision ID: add_validation_jobs
Revises: 
Create Date: 2026-03-30

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'validation_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='QUEUED'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('finished_at', sa.DateTime()),
        sa.Column('error_message', sa.Text()),
    )

def downgrade():
    op.drop_table('validation_jobs')
