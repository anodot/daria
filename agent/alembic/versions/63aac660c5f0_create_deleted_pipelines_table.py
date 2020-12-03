"""create_deleted_pipelines_table

Revision ID: 63aac660c5f0
Revises: 87dc1408358b
Create Date: 2020-12-02 18:04:03.062641

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63aac660c5f0'
down_revision = '87dc1408358b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'deleted_pipelines',
        sa.Column('pipeline_id', sa.String, primary_key=True)
    )


def downgrade():
    op.drop_table('deleted_pipelines')
