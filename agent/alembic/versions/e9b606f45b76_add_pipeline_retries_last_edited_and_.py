"""Add pipeline_retries last_edited and notified flag columns

Revision ID: e9b606f45b76
Revises: 1a2574df7252
Create Date: 2022-04-12 18:53:21.811589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9b606f45b76'
down_revision = '1a2574df7252'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipeline_retries', sa.Column('notification_sent', sa.Boolean, default=False))
    op.add_column('pipeline_retries', sa.Column('last_updated', sa.TIMESTAMP))


def downgrade():
    op.drop_column('pipeline_retries', 'last_updated')
    op.drop_column('pipeline_retries', 'notification_sent')
