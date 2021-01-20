"""add_protocol_column_to_pipelines

Revision ID: 669a641624ed
Revises: 63aac660c5f0
Create Date: 2021-01-20 14:55:47.905829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '669a641624ed'
down_revision = '63aac660c5f0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipelines', sa.Column('protocol', sa.String))


def downgrade():
    op.drop_column('pipelines', 'protocol')
