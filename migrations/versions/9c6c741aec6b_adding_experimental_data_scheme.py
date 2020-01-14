"""Adding Experimental Data Scheme

Revision ID: 9c6c741aec6b
Revises: 03838e8c68e4
Create Date: 2020-01-14 20:58:16.278414

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pgsql


# revision identifiers, used by Alembic.
revision = '9c6c741aec6b'
down_revision = '03838e8c68e4'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()
    op.execute(sa.schema.CreateSequence(sa.Sequence('public.synthesis_id_seq',
        increment=1, start=1, cache=1)))
    op.create_table(
        'synthesis',
        sa.Column('id', sa.Integer, sa.Sequence('public.synthesis_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.synthesis_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('machine_id', pgsql.UUID, nullable=False),
        sa.Column('targeted_molecule_id', pgsql.UUID, nullable=False),
        sa.Column('XDL', sa.Text),
        sa.Column('notes', sa.Text),
        schema='public'
    )


    op.execute(sa.schema.CreateSequence(sa.Sequence('public.synthesis_machine_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'synthesis_machine',
        sa.Column('id', sa.Integer, sa.Sequence('public.synthesis_machine_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.synthesis_machine_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('metadata', pgsql.JSONB),
        sa.Column('lab_id', pgsql.UUID, sa.ForeignKey('public.lab.uuid'), nullable=False),
        schema='public'
    )


    op.execute(sa.schema.CreateSequence(sa.Sequence('public.lab_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'lab',
        sa.Column('id', sa.Integer, sa.Sequence('public.lab_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.lab_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        schema='public'
    )

    op.execute(sa.schema.CreateSequence(sa.Sequence('public.synth_mol_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'synth_molecule',
        sa.Column('id', sa.Integer, sa.Sequence('public.synth_mol_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.synth_mol_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('synth_id', pgsql.UUID, sa.ForeignKey('public.synthesis.uuid'), nullable=False),
        sa.Column('molecule_id', pgsql.UUID, sa.ForeignKey('public.molecule.uuid'), nullable=False),
        sa.Column('yield', sa.Float),
        schema='public'
    )
    
    op.execute(sa.schema.CreateSequence(sa.Sequence('public.synth_fragment_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'synth_fragment',
        sa.Column('id', sa.Integer, sa.Sequence('public.synth_fragment_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.synth_fragment_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('synth_id', pgsql.UUID, sa.ForeignKey('public.synthesis.uuid'), nullable=False),
        sa.Column('fragment_id', pgsql.UUID, sa.ForeignKey('public.fragment.uuid'), nullable=False),
        sa.Column('yield', sa.Float),
        schema='public'
    )



    op.execute(sa.schema.CreateSequence(sa.Sequence('public.experiment_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'experiment',
        sa.Column('id', sa.Integer, sa.Sequence('public.experiment_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.experiment_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('synthesis_id', pgsql.UUID, nullable=False),
        sa.Column('x', pgsql.ARRAY(sa.Float)),
        sa.Column('y', pgsql.ARRAY(sa.Float)),
        sa.Column('x_units_id', pgsql.UUID),
        sa.Column('y_units_id', pgsql.UUID),
        sa.Column('machine_id', pgsql.UUID),
        sa.Column('metadata', pgsql.JSONB, default={}),
        sa.Column('notes', sa.Text, nullable=True),
        schema='public'
    )


    op.execute(sa.schema.CreateSequence(sa.Sequence('public.experiment_machine_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'experiment_machine',
        sa.Column('id', sa.Integer, sa.Sequence('public.experiment_machine_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.experiment_machine_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('metadata', pgsql.JSONB),
        sa.Column('lab_id', pgsql.UUID),
        sa.Column('type_id', pgsql.UUID),
        schema='public'
    )

    
    op.execute(sa.schema.CreateSequence(sa.Sequence('public.experiment_type_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'experiment_type',
        sa.Column('id', sa.Integer, sa.Sequence('public.experiment_type_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.experiment_type_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('x_label', sa.Text, nullable=False),
        sa.Column('y_label', sa.Text, nullable=False),
        schema='public'
    )
   

    op.execute(sa.schema.CreateSequence(sa.Sequence('public.experiment_unit_id_seq', increment=1, start=1, cache=1)))
    op.create_table(
        'experiment_unit',
        sa.Column('id', sa.Integer, sa.Sequence('public.experiment_unit_id_seq'),
            primary_key=True,
            server_default=sa.text("nextval('public.experiment_unit_id_seq'::regclass)")),
        sa.Column('uuid', pgsql.UUID, nullable=False),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        schema='public'
    )

    op.create_foreign_key('lnk_targeted_molecule_synthesis',
                          'public.synthesis',
                          'public.molecule',
                          ['targeted_molecule_id'], ['uuid'])
    op.create_foreign_key('lnk_machine_synthesis',
                          'public.synthesis',
                          'public.synthesis_machine',
                          ['machine_id'], ['uuid'])
    op.create_foreign_key('lnk_synthesis_machine_lab',
                          'public.synthesis_machine',
                          'public.lab',
                          ['lab_id'], ['uuid'])
    op.create_foreign_key('lnk_synthesis_synth_molecule',
                          'public.synth_molecule',
                          'public.synthesis',
                          ['synth_id'], ['uuid'])
    op.create_foreign_key('lnk_synth_molecule_molecule',
                          'public.synth_molecule',
                          'public.molecule',
                          ['molecule_id'], ['uuid'])
    op.create_foreign_key('lnk_synth_fragment_synthesis',
                          'public.synth_fragment',
                          'public.synthesis',
                          ['synth_id'], ['uuid'])
    op.create_foreign_key('lnk_synth_fragment_fragment',
                          'public.synth_fragment',
                          'public.fragment',
                          ['fragment_id'], ['uuid'])
    op.create_foreign_key('lnk_experiment_synthesis',
                          'public.experiment',
                          'public.synthesis',
                          ['synthesis_id'], ['uuid'])
    op.create_foreign_key('lnk_experiment_x_unit',
                          'public.experiment',
                          'public.experiment_unit',
                          ['x_units_id'], ['uuid'])
    op.create_foreign_key('lnk_experiment_y_unit',
                          'public.experiment',
                          'public.experiment_unit',
                          ['y_units_id'], ['uuid'])
    op.create_foreign_key('lnk_experiment_machine',
                          'public.experiment',
                          'public.experiment_machine',
                          ['machine_id'], ['uuid'])
    op.create_foreign_key('lnk_experiment_machine_lab',
                          'public.experiment_machine',
                          'public.lab',
                          ['lab_id'], ['uuid'])
    op.create_foreign_key('lnk_experiment_machine_type',
                          'public.experiment_machine',
                          'public.experiment_type',
                          ['lab_id'], ['uuid'])


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.synthesis_id_seq')))
    op.drop_table('synthesis', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.synthesis_machine_id_seq')))
    op.drop_table('synthesis_machine', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.lab_id_seq')))
    op.drop_table('lab', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.synth_mol_id_seq')))
    op.drop_table('synth_molecule', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.synth_fragment_id_seq')))
    op.drop_table('synth_fragment', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.experiment_id_seq')))
    op.drop_table('experiment', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.experiment_machine_id_seq')))
    op.drop_table('experiment_machine', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.experiment_type_id_seq')))
    op.drop_table('experiment_type', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.experiment_unit_id_seq')))
    op.drop_table('experiment_unit', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequenec('public.synth_mol_id_seq')))
    op.drop_table('synth_molecule', schema='public')


     

def upgrade_madness():
    pass


def downgrade_madness():
    pass


def upgrade_playground():
    pass


def downgrade_playground():
    pass


def upgrade_abqc():
    pass


def downgrade_abqc():
    pass


def upgrade_test():
    pass

def downgrade_test():
    pass
