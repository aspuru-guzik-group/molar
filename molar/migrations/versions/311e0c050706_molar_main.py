"""molar-main

Revision ID: 311e0c050706
Revises: bf3c5d811155
Create Date: 2021-05-26 09:19:46.953180

"""
# external
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pgsql

# revision identifiers, used by Alembic.
revision = "311e0c050706"
down_revision = "bf3c5d811155"
branch_labels = ("molar-main",)
depends_on = None


def upgrade():
    op.execute(
        (
            "create sequence public.molar_database_id_seq"
            "             as integer"
            "   increment by 1"
            "     start with 1"
            "             no minvalue"
            "             no maxvalue"
            "          cache 1;"
        )
    )
    op.create_table(
        "molar_database",
        sa.Column("id", sa.Integer),
        sa.Column("database_name", sa.Text, nullable=False),
        sa.Column("superuser_fullname", sa.Text, nullable=False),
        sa.Column("superuser_email", sa.Text, nullable=False),
        sa.Column("superuser_password", sa.Text, nullable=False),
        sa.Column("alembic_revisions", pgsql.ARRAY(sa.Text), nullable=False),
        sa.Column("is_approved", sa.Boolean, default=False),
        sa.UniqueConstraint("database_name"),
    )

    op.execute(
        "alter sequence public.molar_database_id_seq owned by public.molar_database.id;"
    )
    op.execute(
        (
            "alter table only public.molar_database "
            "    alter column id "
            "     set default nextval('public.molar_database_id_seq'::regclass);"
        )
    )
    op.execute(
        (
            "alter table only public.molar_database "
            " add constraint molar_database_pkey primary key (id);"
        )
    )


def downgrade():
    op.execute("drop sequence public.molar_database_id_seq")
    op.drop_table("molar_database")
