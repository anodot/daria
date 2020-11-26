"""add_schema_column_to_pipelines

Revision ID: 87dc1408358b
Revises: 9d3d42cad294
Create Date: 2020-11-25 15:34:32.641791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87dc1408358b'
down_revision = '9d3d42cad294'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipelines', sa.Column('schema', sa.JSON))


def downgrade():
    op.drop_column('pipelines', 'schema')
