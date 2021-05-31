"""eventsourcing

Revision ID: f31c7d486f1f
Revises: bf3c5d811155
Create Date: 2021-05-26 09:20:26.242476

"""
# external
from alembic import op
import pkg_resources
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f31c7d486f1f"
down_revision = "bf3c5d811155"
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
