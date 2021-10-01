"""make destination_id in pipelines nullable

Revision ID: c069791b5a3b
Revises: 525f87ec086e
Create Date: 2021-09-29 15:50:05.433215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c069791b5a3b'
down_revision = '525f87ec086e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('pipelines', 'destination_id', nullable=True)


def downgrade():
    op.alter_column('pipelines', 'destination_id', nullable=False)
