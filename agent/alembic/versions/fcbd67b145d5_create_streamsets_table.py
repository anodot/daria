"""create_streamsets_table

Revision ID: fcbd67b145d5
Revises: 746f77fcf519
Create Date: 2020-10-21 12:09:06.801304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcbd67b145d5'
down_revision = '746f77fcf519'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'streamsets',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('url', sa.String, nullable=False),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('password', sa.String, nullable=False)
    )


def downgrade():
    op.drop_table('streamsets')
