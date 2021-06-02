"""user-table

Revision ID: bf3c5d811155
Revises: 
Create Date: 2021-05-26 09:19:19.696433

"""
# external
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "bf3c5d811155"
down_revision = None
branch_labels = None
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
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_superuser", sa.Boolean, default=False),
        sa.Column("created_on", sa.DateTime, nullable=False),
        sa.Column("full_name", sa.Text, nullable=False),
        sa.UniqueConstraint("email"),
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
