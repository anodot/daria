"""create pipline notifications table

Revision ID: 971cd06e3d76
Revises: 5bad40f03389
Create Date: 2022-07-04 15:17:14.427408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '971cd06e3d76'
down_revision = '5bad40f03389'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pipeline_notifications',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('pipeline_id', sa.String, nullable=False),
    )

def downgrade():
    op.drop_table('pipeline_notifications')
