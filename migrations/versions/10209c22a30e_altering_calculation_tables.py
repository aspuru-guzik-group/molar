"""Altering calculation tables

Revision ID: 10209c22a30e
Revises: 3a689fa4406c
Create Date: 2020-01-25 21:58:29.282682

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pgsql

# revision identifiers, used by Alembic.
revision = '10209c22a30e'
down_revision = '3a689fa4406c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE calculation DROP COLUMN calculation_type')
    op.execute('DROP TYPE calculation_type CASCADE;')
    op.execute('DROP TYPE calculation_status CASCADE;')

    op.execute('CREATE SEQUENCE public.calculation_type_id_seq AS integer INCREMENT BY 1 START WITH 1 NO MINVALUE NO MAXVALUE CACHE 1;')
    op.create_table(
        'calculation_type',
        sa.Column('id', sa.Integer),
        sa.Column('uuid', pgsql.UUID, nullable=False, unique=True),
        sa.Column('created_on', sa.DateTime, nullable=False),
        sa.Column('updated_on', sa.DateTime, nullable=False),
        sa.Column('name', sa.Text, nullable=False, unique=True),
        schema='public'
    )
    op.execute('ALTER SEQUENCE public.calculation_type_id_seq OWNED BY public.calculation_type.id;')
    op.execute("ALTER TABLE ONLY public.calculation_type ALTER COLUMN id SET DEFAULT nextval('public.calculation_type_id_seq'::regclass);")
    op.execute('ALTER TABLE ONLY public.calculation_type ADD CONSTRAINT calculation_type_pkey PRIMARY KEY (id);')

    op.add_column('calculation',
        sa.Column('calculation_type_id', pgsql.UUID, nullable=False),
        schema='public')

    op.alter_column('calculation', 'properties', new_column_name='metadata')
    
    op.alter_column('molecule', 'properties', new_column_name='metadata')
    op.alter_column('conformation', 'properties', new_column_name='metadata')

    op.execute(('ALTER TABLE ONLY public.calculation ADD CONSTRAINT'
        ' lnk_calculation_type FOREIGN KEY (calculation_type_id)'
        ' REFERENCES public.calculation_type(uuid) MATCH FULL ON UPDATE CASCADE;'))


def downgrade():
    # YOLO!
    pass




def upgrade_madness():
    pass


def downgrade_madness():
    pass


def upgrade_playground():
    pass


def downgrade_playground():
    pass


def upgrade_test():
    pass

def downgrade_test():
    pass
