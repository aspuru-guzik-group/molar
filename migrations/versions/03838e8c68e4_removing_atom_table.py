"""Removing atom table

Revision ID: 03838e8c68e4
Revises: 
Create Date: 2019-10-09 12:48:18.515107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03838e8c68e4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('conformation', sa.Column('coordinates', sa.dialects.postgresql.JSONB), schema='public')
    op.drop_table('atom', schema='public')

def downgrade():
    op.drop_column('conformation', 'coordinates')
    op.execute("""
    CREATE TABLE public.atom (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    updated_on timestamp without time zone NOT NULL,
    created_on timestamp without time zone NOT NULL,
    x real NOT NULL,
    y real NOT NULL,
    z real NOT NULL,
    n integer NOT NULL,
    conformation_id uuid NOT NULL
    );""")
    op.execute("""
    CREATE SEQUENCE public.atom_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
    """)
    op.execute("""ALTER SEQUENCE public.atom_id_seq OWNED BY public.atom.id;""")


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
