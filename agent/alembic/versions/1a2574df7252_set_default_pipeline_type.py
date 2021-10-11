"""set default pipeline type

Revision ID: 1a2574df7252
Revises: c069791b5a3b
Create Date: 2021-10-11 17:58:30.671514

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from agent import pipeline


# revision identifiers, used by Alembic.
revision = '1a2574df7252'
down_revision = 'c069791b5a3b'
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().execute(text(f"UPDATE pipelines SET type = '{pipeline.REGULAR_PIPELINE}' WHERE type IS NULL"))


def downgrade():
    pass
