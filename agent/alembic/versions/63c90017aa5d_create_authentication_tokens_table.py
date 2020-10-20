"""create_authentication_tokens_table

Revision ID: 63c90017aa5d
Revises: b16ba56704dd
Create Date: 2020-10-08 13:44:33.903231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63c90017aa5d'
down_revision = 'b16ba56704dd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'authentication_tokens',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('destination_id', sa.Integer, nullable=False),
        sa.Column('authentication_token', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False)
    )


def downgrade():
    op.drop_table('authentication_tokens')
