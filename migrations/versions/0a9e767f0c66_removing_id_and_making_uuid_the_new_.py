"""Removing id and making uuid the new primary key

Revision ID: 0a9e767f0c66
Revises: c9a2abe13001
Create Date: 2020-02-15 20:52:31.664889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a9e767f0c66'
down_revision = 'c9a2abe13001'
branch_labels = None
depends_on = None


def upgrade():
    table_names = \
            ["conformer", "fragment", "molecule_fragment", "molecule", "software",
             "calculation", "experiment_type", "calculation_type", "synth_molecule",
             "synthesis", "synthesis_machine", "lab", "synth_fragment","experiment", 
             "data_unit", "xy_data", "experiment_machine"]
    for table_name in table_names:
        op.execute(f'alter table public.{table_name} drop column id;')
        op.execute(f'alter table public.{table_name} rename column uuid to id;')
        op.execute(f'alter table public.{table_name} add primary key(id);')


def downgrade():
    # yolo lol!
    pass
