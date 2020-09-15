"""add_created_updated_fields

Revision ID: 9b503e0b17c3
Revises: e3cf0a83f09c
Create Date: 2020-09-15 12:32:09.022769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b503e0b17c3'
down_revision = 'e3cf0a83f09c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE sources ADD COLUMN created_at TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE sources ADD COLUMN last_edited TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE pipelines ADD COLUMN created_at TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE pipelines ADD COLUMN last_edited TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE destinations ADD COLUMN created_at TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE destinations ADD COLUMN last_edited TIMESTAMP WITH TIME ZONE')


def downgrade():
    op.execute('ALTER TABLE sources DROP COLUMN created_at')
    op.execute('ALTER TABLE sources DROP COLUMN last_edited')
    op.execute('ALTER TABLE pipelines DROP COLUMN created_at')
    op.execute('ALTER TABLE pipelines DROP COLUMN last_edited')
    op.execute('ALTER TABLE destinations DROP COLUMN created_at')
    op.execute('ALTER TABLE destinations DROP COLUMN last_edited')
