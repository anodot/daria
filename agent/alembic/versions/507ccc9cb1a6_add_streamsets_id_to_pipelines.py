"""add_streamsets_id_to_pipelines

Revision ID: 507ccc9cb1a6
Revises: fcbd67b145d5
Create Date: 2020-10-21 15:14:37.225799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '507ccc9cb1a6'
down_revision = 'fcbd67b145d5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipelines', sa.Column('streamsets_id', sa.Integer))
    op.create_foreign_key('fk_streamsets_id', 'pipelines', 'streamsets', ['streamsets_id'], ['id'])


def downgrade():
    op.drop_column('streamsets', 'streamsets_id')
