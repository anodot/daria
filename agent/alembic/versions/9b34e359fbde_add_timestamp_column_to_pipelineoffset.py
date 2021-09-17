"""add timestamp column to PipelineOffset

Revision ID: 9b34e359fbde
Revises: d04cf726555d
Create Date: 2021-09-17 13:03:02.676455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b34e359fbde'
down_revision = 'd04cf726555d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipeline_offsets', sa.Column('timestamp', sa.Float))


def downgrade():
    op.drop_column('pipeline_offsets', 'timestamp')
