"""synthesis.xdl type test -> xml

Revision ID: 4f9307d07ff9
Revises: 0a9e767f0c66
Create Date: 2020-02-15 22:53:27.762311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f9307d07ff9'
down_revision = '0a9e767f0c66'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('alter table public.synthesis alter column xdl type xml using xdl::xml;');


def downgrade():
    # still not going to write a downgrade now...
    pass
