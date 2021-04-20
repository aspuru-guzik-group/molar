"""user-table

Revision ID: fb3f43ec8aaa
Revises: c59a26437bf4
Create Date: 2021-04-20 11:45:31.260835

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fb3f43ec8aaa"
down_revision = "c59a26437bf4"
branch_labels = ("user-table",)
depends_on = None


def upgrade():
    op.execute('create schema "user"')
    op.execute(
        (
            'create sequence "user".user_id_seq'
            "             as integer"
            "   increment by 1"
            "       start with 1"
            "          no minvalue"
            "          no maxvalue"
            "       cache 1;"
        )
    )
    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer),
        sa.Column("email", sa.Text, unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_superuser", sa.Boolean, default=False),
        sa.Column("created_on", sa.DateTime, nullable=False),
        schema="user",
    )

    op.execute('alter sequence "user".user_id_seq owned by "user".user.user_id;')
    op.execute(
        (
            'alter table only "user".user '
            "    alter column user_id"
            "     set default nextval('\"user\".user_id_seq'::regclass);"
        )
    )
    op.execute(
        'alter table only "user".user '
        "  add constraint user_pkey primary key (user_id);"
    )


def downgrade():
    op.execute('drop sequence "user".user_id_seq')
    op.drop_table("user")
    op.execute('drop schema "user" cascade')
