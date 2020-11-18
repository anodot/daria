"""change_offset_column_to_dict

Revision ID: 7f83337f206b
Revises: 9d3d42cad294
Create Date: 2020-11-18 15:19:20.588551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f83337f206b'
down_revision = '9d3d42cad294'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('pipeline_offsets', 'offset')
    op.add_column('pipeline_offsets', sa.Column('offset', sa.JSON))


def downgrade():
    op.add_column('pipeline_offsets', sa.Column('offset', sa.String))
    op.drop_column('pipeline_offsets', 'offset')
