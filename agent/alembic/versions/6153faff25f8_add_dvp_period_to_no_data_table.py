"""add_dvp_period_to_no_data_table

Revision ID: 6153faff25f8
Revises: f6e29156129d
Create Date: 2022-08-10 14:51:49.403014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6153faff25f8'
down_revision = '0684b9e43e95'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('no_data_notifications', sa.Column('dvp_notification_period', sa.Integer))
    op.execute('UPDATE no_data_notifications SET dvp_notification_period=1440')


def downgrade():
    op.drop_column('no_data_notifications', 'dvp_notification_period')
