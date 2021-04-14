"""create cacti_metadata_cache table

Revision ID: fc92fa8ed02b
Revises: 63aac660c5f0
Create Date: 2021-03-26 12:25:36.988744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc92fa8ed02b'
down_revision = '63aac660c5f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cacti_cache',
        sa.Column('pipeline_id', sa.String, primary_key=True),
        sa.Column('data', sa.JSON, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False)
    )


def downgrade():
    op.drop_table('cacti_cache')
