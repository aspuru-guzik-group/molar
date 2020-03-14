"""modification from the workshop

Revision ID: 9166672ddef8
Revises: 4f9307d07ff9
Create Date: 2020-03-02 20:08:28.743631

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = '9166672ddef8'
down_revision = '4f9307d07ff9'
branch_labels = None
depends_on = None


def upgrade():
    # Molecule - Fragment -> Molecule - Molecule Type
    op.drop_table('molecule_fragment')
    op.drop_table('synth_fragment')
    op.drop_table('fragment')
    op.create_table('molecule_type',
                    sa.Column('molecule_type_id', pg.UUID, primary_key=True, nullable=False),
                    sa.Column('created_on', sa.DateTime, nullable=False),
                    sa.Column('updated_on', sa.DateTime, nullable=False),
                    sa.Column('name', sa.Text, nullable=False))

    op.add_column('molecule',
                  sa.Column('molecule_type_id', pg.UUID))

    op.add_column('molecule',
                  sa.Column('cas', sa.Text, nullable=True))

    op.add_column('molecule',
                  sa.Column('cid', sa.Integer, nullable=True))

    op.add_column('molecule',
                  sa.Column('inchi', sa.Text, nullable=True))

    op.add_column('molecule',
                  sa.Column('iupac_name', sa.Text, nullable=True))

    op.execute((' alter table only public.molecule\n'
                '   add constraint lnk_molecule_molecule_type\n'
                '      foreign key (molecule_type_id)\n'
                '       references public.molecule_type(molecule_type_id)\n'
                '       match full on update cascade;'))
    op.create_table('molecule_molecule',
                    sa.Column('molecule_molecule_id', pg.UUID, nullable=False),
                    sa.Column('reactant_molecule_id', pg.UUID, nullable=False),
                    sa.Column('product_molecule_id', pg.UUID, nullable=False),
                    sa.Column('order', sa.Integer, nullable=False))
    op.execute((' alter table only public.molecule_molecule\n'
                '   add constraint lnk_reactant_molecule_id\n'
                '      foreign key (reactant_molecule_id)\n'
                '       references public.molecule(molecule_id),\n'
                '   add constraint lnk_product_molecule_id\n'
                '      foreign key (product_molecule_id)\n'
                '       references public.molecule(molecule_id),\n'
                '   add constraint molecule_molecule_pkey\n'
                '      primary key (reactant_molecule_id,\n'
                '                   product_molecule_id,\n'
                '                   "order")\n'))

    # Experiment_machine and Synthesis_machine
    #   -> Adding make and model

    op.add_column('experiment_machine',
                  sa.Column('make', sa.Text))

    op.add_column('experiment_machine',
                  sa.Column('model', sa.Text))
    op.add_column('synthesis_machine',
                  sa.Column('make', sa.Text))
    op.add_column('synthesis_machine',
                  sa.Column('model', sa.Text))

    # Experiment
    #   -> Adding a link to previous experiment
    #   -> Adding relationship to molecule_id
    #   -> Adding a constrain (synthesis_id, molecule_id) not null
    #   -> Adding experiment timestamp
    #   -> raw_data_filename
    op.add_column('experiment',
                  sa.Column('parent_experiment_id', pg.UUID, nullable=True))
    op.add_column('experiment',
                  sa.Column('molecule_id', pg.UUID))
    op.add_column('experiment',
                  sa.Column('experiment_timestamp', sa.DateTime))
    op.add_column('experiment',
                  sa.Column('raw_data_path', sa.Text, nullable=True))

    op.execute((' alter table only experiment\n'
                '   add constraint lnk_parent_experiment_id\n'
                '      foreign key (parent_experiment_id)\n'
                '       references public.experiment(experiment_id),\n'
                '   add constraint lnk_experiment_molecule_id\n'
                '      foreign key (molecule_id)\n'
                '       references public.molecule(molecule_id),\n'
                '   add constraint check_synthesis_id_molecule_id_not_null \n'
                '            check (num_nonnulls(molecule_id, synthesis_id) = 1);\n'))
    op.execute('alter table only experiment alter column synthesis_id drop not null')

    # Adding xyz table
    #   -> linked to both experiment and calculation
    op.create_table('xyz_data',
                    sa.Column('xyz_data_id', pg.UUID, primary_key=True, nullable=False), 
                    sa.Column('created_on', sa.DateTime, nullable=False),
                    sa.Column('updated_on', sa.DateTime, nullable=False),
                    sa.Column('x', pg.ARRAY(sa.Float), nullable=False),
                    sa.Column('y', pg.ARRAY(sa.Float), nullable=False),
                    sa.Column('z', pg.ARRAY(sa.Float), nullable=False),
                    sa.Column('x_units_id', pg.UUID),
                    sa.Column('y_units_id', pg.UUID),
                    sa.Column('z_units_id', pg.UUID),
                    sa.Column('experiment_id', pg.UUID),
                    sa.Column('calculation_id', pg.UUID),
                    sa.Column('metadata', pg.JSONB, default={}),
                    sa.Column('notes', sa.Text, nullable=True))
    op.execute(('alter table only xyz_data\n'
                '  add constraint lnk_xyz_data_x_units\n'
                '     foreign key (x_units_id)\n'
                '      references public.data_unit(data_unit_id),\n'
                '  add constraint lnk_xyz_data_y_units\n'
                '     foreign key (y_units_id)\n'
                '      references public.data_unit(data_unit_id),\n'
                '  add constraint lnk_xyz_data_z_units\n'
                '     foreign key (z_units_id)\n'
                '      references public.data_unit(data_unit_id),\n'
                '  add constraint lnk_xyz_data_calculation\n'
                '     foreign key (calculation_id)\n'
                '      references public.calculation(calculation_id),\n'
                '  add constraint lnk_xyz_data_experiment\n'
                '     foreign key (experiment_id)\n'
                '      references public.experiment(experiment_id),\n'
                '  add constraint xyz_data_calculation_or_experiment\n'
                '           check (num_nonnulls(calculation_id, experiment_id) = 1)\n'))

    # Change molecule -> conformation MM relationship that can also be null
    op.drop_column('conformer', 'molecule_id')
    op.create_table('conformer_molecule',
                    sa.Column('conformer_molecule_id', pg.UUID, nullable=False),
                    sa.Column('conformer_id', pg.UUID, nullable=False),
                    sa.Column('molecule_id', pg.UUID, nullable=False))

    op.create_primary_key('conformer_molecule_pkey', 'conformer_molecule',
                          ['conformer_id', 'molecule_id'])
    op.execute(('alter table only conformer_molecule \n'
                '  add constraint lnk_molecule_conformer \n'
                '     foreign key (conformer_id) \n'
                '      references public.conformer(conformer_id),\n'
                '  add constraint lnk_conformer_molecule\n'
                '     foreign key (molecule_id)\n'
                '      references public.molecule(molecule_id)\n'))


def downgrade():
    # Still not gonna implement that now
    pass
