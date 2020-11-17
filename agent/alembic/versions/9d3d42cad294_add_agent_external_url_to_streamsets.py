"""add_agent_external_url_to_streamsets

Revision ID: 9d3d42cad294
Revises: 507ccc9cb1a6
Create Date: 2020-11-13 13:05:40.922113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d3d42cad294'
down_revision = '507ccc9cb1a6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('streamsets', sa.Column('agent_external_url', sa.String, nullable=False))


def downgrade():
    op.drop_column('streamsets', 'agent_external_url')
