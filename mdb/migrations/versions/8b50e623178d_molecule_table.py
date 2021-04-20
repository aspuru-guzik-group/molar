"""molecule table

Revision ID: 8b50e623178d
Revises: fb3f43ec8aaa
Create Date: 2021-03-24 17:09:37.477651

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pgsql

# revision identifiers, used by Alembic.
revision = "8b50e623178d"
down_revision = "fb3f43ec8aaa"
branch_labels = ("molecule-table",)
depends_on = None


def upgrade():
    op.create_table(
        "molecule",
        sa.Column("molecule_id", pgsql.UUID, primary_key=True, nullable=True),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("metadata", pgsql.JSONB),
        sa.Column("smiles", sa.Text, nullable=False, unique=True),
        schema="public",
    )


def downgrade():
    op.drop_table("molecule")
