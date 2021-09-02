"""create pipeline_retries table

Revision ID: d04cf726555d
Revises: fc92fa8ed02b
Create Date: 2021-09-02 13:04:36.053768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd04cf726555d'
down_revision = 'fc92fa8ed02b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pipeline_retries',
        sa.Column('pipeline_id', sa.String, nullable=False),
        sa.Column('number_of_error_statuses', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('pipeline_retries')
