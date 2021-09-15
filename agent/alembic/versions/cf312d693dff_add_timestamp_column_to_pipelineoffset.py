"""add timestamp column to PipelineOffset

Revision ID: cf312d693dff
Revises: fc92fa8ed02b
Create Date: 2021-09-15 15:00:34.795316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf312d693dff'
down_revision = 'fc92fa8ed02b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipeline_offsets', sa.Column('timestamp', sa.Float))


def downgrade():
    op.drop_column('pipeline_offsets', 'timestamp')
