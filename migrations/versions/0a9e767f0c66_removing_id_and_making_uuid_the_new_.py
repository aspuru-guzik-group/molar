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
    # id -> table_name_id so we can use select * from a join b using (table_name_id)
    table_names = \
            ["conformer", "fragment", "molecule_fragment", "molecule", "software",
             "calculation", "experiment_type", "calculation_type", "synth_molecule",
             "synthesis", "synthesis_machine", "lab", "synth_fragment","experiment", 
             "data_unit", "xy_data", "experiment_machine"]
    for table_name in table_names:
        op.execute(f'alter table public.{table_name} drop column id;')
        op.execute(f'alter table public.{table_name} rename column uuid to {table_name}_id;')
        op.execute(f'alter table public.{table_name} add primary key({table_name}_id);')

    # also renaming some keys
    op.execute('alter table public.synthesis rename column machine_id to synthesis_machine_id')
    op.execute('alter table public.experiment_machine rename column type_id to experiment_type_id')
    op.execute('alter table public.synthesis rename column targeted_molecule_id to molecule_id')
    op.execute('alter table public.experiment rename column synth_id to synthesis_id')
    op.execute('alter table public.synth_molecule rename column synth_id to synthesis_id')
    op.execute('alter table public.synth_fragment rename column  synth_id to synthesis_id ')
    op.execute('alter table public.experiment rename column machine_id to experiment_machine_id')
    op.execute('alter table public.fragment rename column properties to metadata')

def downgrade():
    # yolo lol!
    pass
