"""create pipeline_watermarks table

Revision ID: 5bad40f03389
Revises: e9b606f45b76
Create Date: 2022-04-28 15:33:17.951668

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5bad40f03389'
down_revision = 'e9b606f45b76'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pipeline_watermarks', sa.Column('pipeline_id', sa.String(), primary_key=True),
        sa.Column('timestamp', sa.Float, nullable=False)
    )
    op.create_foreign_key(
        'fk_pipeline_watermarks_pipeline', 'pipeline_watermarks', 'pipelines', ['pipeline_id'], ['name']
    )


def downgrade():
    op.drop_table('pipeline_watermarks')
