"""eventsourcing

Revision ID: c59a26437bf4
Revises: 
Create Date: 2021-03-24 15:27:53.540069

"""
import pkg_resources
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c59a26437bf4"
down_revision = None
branch_labels = ("eventsourcing",)
depends_on = None


def upgrade():
    filename = pkg_resources.resource_filename("molar", "sql/event_sourcing.sql")
    sql = open(filename, "r").read()
    op.execute(sql)


def downgrade():
    op.execute("drop table if exists sourcing.eventstore")
    op.execute("drop sequence if exists sourcing.eventstore_id_seq")
    op.execute('drop schema "sourcing" cascade')
