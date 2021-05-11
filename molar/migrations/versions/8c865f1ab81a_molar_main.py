"""molar-main

Revision ID: 8c865f1ab81a
Revises: fb3f43ec8aaa
Create Date: 2021-04-21 15:04:52.892851

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pgsql

# revision identifiers, used by Alembic.
revision = "8c865f1ab81a"
down_revision = "fb3f43ec8aaa"
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
        sa.Column("database_name", sa.Text, unique=True, index=True, nullable=False),
        sa.Column("superuser_fullname", sa.Text, nullable=False),
        sa.Column("superuser_email", sa.Text, nullable=False),
        sa.Column("superuser_password", sa.Text, nullable=False),
        sa.Column("alembic_revisions", pgsql.ARRAY(sa.Text), nullable=False),
        sa.Column("is_approved", sa.Boolean, default=False),
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
