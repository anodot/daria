"""create no data notification table

Revision ID: 0684b9e43e95
Revises: 971cd06e3d76
Create Date: 2022-07-04 15:20:43.836987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0684b9e43e95'
down_revision = '971cd06e3d76'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'no_data_notifications',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('pipeline_id', sa.String, nullable=False),
        sa.Column('notification_id', sa.Integer, sa.ForeignKey('pipeline_notifications.id')),
        sa.Column('notification_period', sa.Integer, nullable=False),
        sa.Column('notification_sent', sa.Boolean, default=False),
        sa.Column('last_updated', sa.TIMESTAMP),
    )


def downgrade():
    op.drop_table('no_data_notifications')
