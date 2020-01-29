"""Removing the need of a user in the eventstore

Revision ID: 3a689fa4406c
Revises: 9c6c741aec6b
Create Date: 2020-01-19 21:15:48.403921

"""
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = '3a689fa4406c'
down_revision = '9c6c741aec6b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('eventstore', schema='sourcing')
    op.drop_column('calculation', 'user_id', schema='public')
    op.drop_table('user', schema='public')
    es_script = os.path.join(os.path.dirname(__file__), '../../pgsql/event_sourcing.sql')
    es_script = open(es_script, 'r').read()
    op.execute(es_script)


def downgrade():
    pass
