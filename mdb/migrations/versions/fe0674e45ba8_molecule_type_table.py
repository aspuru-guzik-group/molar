"""molecule_type table

Revision ID: fe0674e45ba8
Revises: fb3f43ec8aaa
Create Date: 2021-03-24 17:21:45.544702

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pgsql

# revision identifiers, used by Alembic.
revision = "fe0674e45ba8"
down_revision = "fb3f43ec8aaa"
branch_labels = ("molecule-type",)
depends_on = "8b50e623178d"


def upgrade():
    op.create_table(
        "molecule_type",
        sa.Column("molecule_type_id", pgsql.UUID, primary_key=True, nullable=True),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("metadata", pgsql.JSONB),
        sa.Column("name", sa.Text, nullable=False, unique=True),
    )

    op.add_column(
        "molecule",
        sa.Column(
            "molecule_type_id",
            pgsql.UUID,
            sa.ForeignKey("molecule_type.molecule_type_id"),
        ),
    )


def downgrade():
    op.drop_column("molecule", "molecule_type_id")
    op.drop_table("molecule_type")
