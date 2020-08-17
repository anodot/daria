"""create destinations sources pipelines table

Revision ID: e3cf0a83f09c
Revises: 
Create Date: 2020-08-17 11:43:54.446937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3cf0a83f09c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'destinations',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('host_id', sa.String, nullable=False),
        sa.Column('access_key', sa.String),
        sa.Column('config', sa.JSON, nullable=False)
    )
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('config', sa.JSON, nullable=False)
    )
    op.create_table(
        'pipelines',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('source_id', sa.Integer, nullable=False),
        sa.Column('config', sa.JSON, nullable=False)
    )
    op.create_foreign_key('fk_source_pipeline', 'pipelines', 'sources', ['source_id'], ['id'])


def downgrade():
    pass
