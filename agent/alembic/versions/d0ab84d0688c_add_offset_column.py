"""add_offset_column

Revision ID: d0ab84d0688c
Revises: b16ba56704dd
Create Date: 2020-10-06 11:33:36.305823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0ab84d0688c'
down_revision = 'b16ba56704dd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipelines', sa.Column('offset', sa.String))


def downgrade():
    op.drop_column('pipelines', 'offset')
