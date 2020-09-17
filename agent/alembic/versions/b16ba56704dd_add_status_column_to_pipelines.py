"""add status column to pipelines

Revision ID: b16ba56704dd
Revises: 9b503e0b17c3
Create Date: 2020-09-17 11:32:35.943148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b16ba56704dd'
down_revision = '9b503e0b17c3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipelines', sa.Column('status', sa.String))


def downgrade():
    op.drop_column('pipelines', 'status')
