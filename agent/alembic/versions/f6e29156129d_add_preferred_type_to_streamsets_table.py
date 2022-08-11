"""add preferred type to streamsets table

Revision ID: f6e29156129d
Revises: 0684b9e43e95
Create Date: 2022-08-03 11:33:17.038360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6e29156129d'
down_revision = '0684b9e43e95'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('streamsets', sa.Column('preferred_type', sa.String, nullable=True))


def downgrade():
    op.drop_column('streamsets', 'preferred_type')
