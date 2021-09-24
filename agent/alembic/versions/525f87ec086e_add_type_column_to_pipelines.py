"""add type column to pipelines

Revision ID: 525f87ec086e
Revises: 9b34e359fbde
Create Date: 2021-09-23 16:08:34.060496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '525f87ec086e'
down_revision = '9b34e359fbde'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipelines', sa.Column('type', sa.String))


def downgrade():
    op.drop_column('streamsets', 'type')
