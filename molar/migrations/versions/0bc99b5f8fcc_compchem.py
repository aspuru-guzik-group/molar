"""compchem

Revision ID: 0bc99b5f8fcc
Revises: f31c7d486f1f
Create Date: 2021-05-26 09:27:03.263583

"""
# external
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pgsql

# revision identifiers, used by Alembic.
revision = "0bc99b5f8fcc"
down_revision = "f31c7d486f1f"
branch_labels = ("compchem",)
depends_on = None


def upgrade():
    op.create_table(
        "molecule",
        sa.Column("molecule_id", pgsql.UUID, primary_key=True, nullable=False),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("metadata", pgsql.JSONB),
        sa.Column("smiles", sa.Text, nullable=False, unique=True),
        schema="public",
    )

    op.create_table(
        "molecule_type",
        sa.Column("molecule_type_id", pgsql.UUID, primary_key=True, nullable=False),
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

    op.create_table(
        "conformer",
        sa.Column("conformer_id", pgsql.UUID, primary_key=True, nullable=False),
        sa.Column("molecule_id", pgsql.UUID, sa.ForeignKey("molecule.molecule_id")),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("metadata", pgsql.JSONB),
        sa.Column("x", pgsql.ARRAY(sa.Float), nullable=False),
        sa.Column("y", pgsql.ARRAY(sa.Float), nullable=False),
        sa.Column("z", pgsql.ARRAY(sa.Float), nullable=False),
        sa.Column("atomic_numbers", pgsql.ARRAY(sa.Integer), nullable=False),
    )

    op.create_table(
        "software",
        sa.Column("software_id", pgsql.UUID, primary_key=True, nullable=True),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("version", sa.Text, nullable=False),
        sa.UniqueConstraint("name", "version", name="software_name_version_unique"),
    )

    op.create_table(
        "calculation",
        sa.Column("calculation_id", pgsql.UUID, primary_key=True, nullable=False),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("metadata", pgsql.JSONB),
        sa.Column(
            "conformer_id",
            pgsql.UUID,
            sa.ForeignKey("conformer.conformer_id"),
            nullable=False,
        ),
        sa.Column(
            "software_id",
            pgsql.UUID,
            sa.ForeignKey("software.software_id"),
            nullable=False,
        ),
        sa.Column(
            "output_conformer_id",
            pgsql.UUID,
            sa.ForeignKey("conformer.conformer_id"),
            nullable=True,
        ),
        sa.Column("input_file", sa.Text, nullable=True),
        sa.Column("command_line", sa.Text, nullable=True),
    )

    op.create_table(
        "numerical_data",
        sa.Column("numerical_data_id", pgsql.UUID, primary_key=True, nullable=False),
        sa.Column(
            "calculation_id",
            pgsql.UUID,
            sa.ForeignKey("calculation.calculation_id"),
            nullable=False,
        ),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("updated_on", sa.DateTime, nullable=False),
        sa.Column("metadata", pgsql.JSONB),
        sa.Column("data", pgsql.ARRAY(sa.Float)),
    )


def downgrade():
    op.drop_table("numerical_data")
    op.drop_table("calculation")
    op.drop_table("software")
    op.drop_table("conformer")
    op.drop_column("molecule", "molecule_type_id")
    op.drop_table("molecule_type")
    op.drop_table("molecule")
