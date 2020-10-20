"""create_pipeline_offset_table

Revision ID: 746f77fcf519
Revises: 63c90017aa5d
Create Date: 2020-10-20 13:32:59.329693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '746f77fcf519'
down_revision = '63c90017aa5d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pipeline_offsets',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('pipeline_id', sa.Integer, nullable=False),
        sa.Column('offset', sa.String, nullable=False)
    )


def downgrade():
    op.drop_table('pipeline_offsets')
