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
    op.execute('CREATE SEQUENCE public.synthesis_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'synthesis',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('hid', sa.String(16), nullable=False),
        sa.Column('machine_id', pgsql.UUID, nullable=False),
        sa.Column('targeted_molecule_id', pgsql.UUID, nullable=False),
        sa.Column('xdl', sa.Text),
        sa.Column('notes', sa.Text),
        schema='public'
    )
    op.execute('ALTER SEQUENCE public.synthesis_id_seq OWNED BY public.synthesis.id;')
    op.execute("ALTER TABLE ONLY public.synthesis ALTER COLUMN id SET DEFAULT nextval('public.synthesis_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.synthesis ADD CONSTRAINT synthesis_pkey PRIMARY KEY (id);')

    op.execute('CREATE SEQUENCE public.synthesis_machine_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'synthesis_machine',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('metadata', pgsql.JSONB),
        sa.Column('lab_id', pgsql.UUID, nullable=False),
        schema='public'
    )

    op.execute('ALTER SEQUENCE public.synthesis_machine_id_seq OWNED BY public.synthesis_machine.id;')
    op.execute("ALTER TABLE ONLY public.synthesis_machine ALTER COLUMN id SET DEFAULT nextval('public.synthesis_machine_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.synthesis_machine ADD CONSTRAINT syntheis_machine_pkey PRIMARY KEY (id);')

    op.execute('CREATE SEQUENCE public.lab_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'lab',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('short_name', sa.String(3), nullable=False, unique=True),
        sa.Column('name', sa.Text, nullable=False),
        schema='public'
    )


    op.execute('ALTER SEQUENCE public.lab_id_seq OWNED BY public.lab.id;')
    op.execute("ALTER TABLE ONLY public.lab ALTER COLUMN id SET DEFAULT nextval('public.lab_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.lab ADD CONSTRAINT lab_pkey PRIMARY KEY (id);')

    op.execute('CREATE SEQUENCE public.synth_molecule_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'synth_molecule',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('synth_id', pgsql.UUID, nullable=False),
        sa.Column('molecule_id', pgsql.UUID, nullable=False),
        sa.Column('yield', sa.Float),
        schema='public'
    )


    op.execute('ALTER SEQUENCE public.synth_molecule_id_seq OWNED BY public.synth_molecule.id;')
    op.execute("ALTER TABLE ONLY public.synth_molecule ALTER COLUMN id SET DEFAULT nextval('public.synth_molecule_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.synth_molecule ADD CONSTRAINT synth_molecule_pkey PRIMARY KEY (id);')

    op.execute('CREATE SEQUENCE public.synth_fragment_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'synth_fragment',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('synth_id', pgsql.UUID, nullable=False),
        sa.Column('fragment_id', pgsql.UUID, nullable=False),
        sa.Column('yield', sa.Float),
        schema='public'
    )


    op.execute('ALTER SEQUENCE public.synth_fragment_id_seq OWNED BY public.synth_fragment.id;')
    op.execute("ALTER TABLE ONLY public.synth_fragment ALTER COLUMN id SET DEFAULT nextval('public.synth_fragment_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.synth_fragment ADD CONSTRAINT synth_fragment_pkey PRIMARY KEY (id);')


    op.execute('CREATE SEQUENCE public.experiment_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'experiment',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('synth_id', pgsql.UUID, nullable=False),
        sa.Column('machine_id', pgsql.UUID),
        sa.Column('metadata', pgsql.JSONB, default={}),
        sa.Column('notes', sa.Text, nullable=True),
        schema='public'
    )

    op.execute('ALTER SEQUENCE public.experiment_id_seq OWNED BY public.experiment.id;')
    op.execute("ALTER TABLE ONLY public.experiment ALTER COLUMN id SET DEFAULT nextval('public.experiment_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.experiment ADD CONSTRAINT experiment_pkey PRIMARY KEY (id);')

    op.execute('CREATE SEQUENCE public.xy_data_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'xy_data',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('experiment_id', pgsql.UUID),
        sa.Column('calculation_id', pgsql.UUID),
        sa.Column('x', pgsql.ARRAY(sa.Float), nullable=False),
        sa.Column('y', pgsql.ARRAY(sa.Float), nullable=False),
        sa.Column('x_units_id', pgsql.UUID),
        sa.Column('y_units_id', pgsql.UUID),
        sa.Column('metadata', pgsql.JSONB, default={}),
        sa.Column('notes', sa.Text, nullable=True),
        schema='public'
    )

    op.execute('ALTER SEQUENCE public.experiment_id_seq OWNED BY public.xy_data.id;')
    op.execute("ALTER TABLE ONLY public.xy_data ALTER COLUMN id SET DEFAULT nextval('public.xy_data_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.xy_data ADD CONSTRAINT xy_data_pkey PRIMARY KEY (id);')
    

    op.execute('CREATE SEQUENCE public.experiment_machine_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'experiment_machine',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('metadata', pgsql.JSONB),
        sa.Column('lab_id', pgsql.UUID, nullable=False),
        sa.Column('type_id', pgsql.UUID, nullable=False),
        schema='public'
    )

    op.execute('ALTER TABLE ONLY public.experiment_machine ADD CONSTRAINT unique_lab_id_type_id_name UNIQUE (name, lab_id, type_id)') 


    op.execute('ALTER SEQUENCE public.experiment_machine_id_seq OWNED BY public.experiment_machine.id;')
    op.execute("ALTER TABLE ONLY public.experiment_machine ALTER COLUMN id SET DEFAULT nextval('public.experiment_machine_id_seq'::regclass);") 
    op.execute('ALTER TABLE ONLY public.experiment_machine ADD CONSTRAINT experiment_machine_pkey PRIMARY KEY (id);')

    op.execute('CREATE SEQUENCE public.experiment_type_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'experiment_type',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        schema='public'
    )


    op.execute('ALTER SEQUENCE public.experiment_type_id_seq OWNED BY public.experiment_type.id;')
    op.execute("ALTER TABLE ONLY public.experiment_type ALTER COLUMN id SET DEFAULT nextval('public.experiment_type_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.experiment_type ADD CONSTRAINT experiment_type_pkey PRIMARY KEY (id);')


    op.execute('CREATE SEQUENCE public.data_unit_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'data_unit',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False, unique=True),
        schema='public'
    )


    op.execute('ALTER SEQUENCE public.data_unit_id_seq OWNED BY public.data_unit.id;')
    op.execute("ALTER TABLE ONLY public.data_unit ALTER COLUMN id SET DEFAULT nextval('public.data_unit_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.data_unit ADD CONSTRAINT data_unit_pkey PRIMARY KEY (id);')
    
    op.execute(('ALTER TABLE ONLY public.synthesis ADD CONSTRAINT'
    ' lnk_targeted_molecule_synthesis FOREIGN KEY (targeted_molecule_id)'
    ' REFERENCES public.molecule(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.synthesis ADD CONSTRAINT'
    ' lnk_machine_synthesis FOREIGN KEY (machine_id)'
    ' REFERENCES public.synthesis_machine(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.synthesis_machine ADD CONSTRAINT'
    ' lnk_synthesis_machine_lab FOREIGN KEY (lab_id)'
    ' REFERENCES public.lab(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.synth_molecule ADD CONSTRAINT'
    ' lnk_synthesis_synth_molecule FOREIGN KEY (synth_id)'
    ' REFERENCES public.synthesis(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.synth_molecule ADD CONSTRAINT'
    ' lnk_synth_molecule_molecule FOREIGN KEY (molecule_id)'
    ' REFERENCES public.molecule(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.synth_fragment ADD CONSTRAINT'
    ' lnk_synth_fragment_synthesis FOREIGN KEY (synth_id)'
    ' REFERENCES public.synthesis(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.synth_fragment ADD CONSTRAINT'
    ' lnk_synth_fragment_fragment FOREIGN KEY (fragment_id)'
    ' REFERENCES public.fragment(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.experiment ADD CONSTRAINT'
    ' lnk_experiment_synthesis FOREIGN KEY (synth_id)'
    ' REFERENCES public.synthesis(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.xy_data ADD CONSTRAINT'
    ' lnk_xy_data_x_unit FOREIGN KEY (x_units_id)'
    ' REFERENCES public.data_unit(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.xy_data ADD CONSTRAINT'
    ' lnk_xy_data_y_unit FOREIGN KEY (y_units_id)'
    ' REFERENCES public.data_unit(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.xy_data ADD CONSTRAINT'
    ' lnk_xy_data_experiment FOREIGN KEY (experiment_id)'
    ' REFERENCES public.experiment(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.xy_data ADD CONSTRAINT'
    ' lnk_xy_data_computation FOREIGN KEY (calculation_id)'
    ' REFERENCES public.calculation(uuid) MATCH FULL ON UPDATE CASCADE;'))
    
    op.execute(('ALTER TABLE ONLY public.experiment ADD CONSTRAINT'
    ' lnk_experiment_machine FOREIGN KEY (machine_id)'
    ' REFERENCES public.experiment_machine(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.experiment_machine ADD CONSTRAINT'
    ' lnk_experiment_machine_lab FOREIGN KEY (lab_id)'
    ' REFERENCES public.lab(uuid) MATCH FULL ON UPDATE CASCADE;'))

    op.execute(('ALTER TABLE ONLY public.experiment_machine ADD CONSTRAINT'
    ' lnk_experiment_machine_type FOREIGN KEY (type_id)'
    ' REFERENCES public.experiment_type(uuid) MATCH FULL ON UPDATE CASCADE;'))


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()

    op.execute(sa.schema.DropSequence(sa.Sequence('public.synthesis_id_seq')))
    op.drop_table('synthesis', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.synthesis_machine_id_seq')))
    op.drop_table('synthesis_machine', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.lab_id_seq')))
    op.drop_table('lab', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.synth_mol_id_seq')))
    op.drop_table('synth_molecule', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.synth_fragment_id_seq')))
    op.drop_table('synth_fragment', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.experiment_id_seq')))
    op.drop_table('experiment', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.experiment_machine_id_seq')))
    op.drop_table('experiment_machine', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.experiment_type_id_seq')))
    op.drop_table('experiment_type', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.data_unit_id_seq')))
    op.drop_table('data_unit', schema='public')

    op.execute(sa.schema.DropSequence(sa.Sequence('public.synth_mol_id_seq')))
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
