# std
from datetime import datetime

# external
from alembic import command
from pydantic import PostgresDsn
from sqlalchemy import text

from . import sql_utils


def install_molar_database(
    alembic_config,
    hostname,
    postgres_username,
    postgres_password,
    new_database_name,
    superuser_fullname,
    superuser_email,
    superuser_hashed_password,
    revisions,
):
    create_database(
        alembic_config,
        hostname,
        postgres_username,
        postgres_password,
        new_database_name,
        revisions,
    )
    add_user(
        superuser_fullname,
        superuser_email,
        superuser_hashed_password,
        hostname,
        postgres_username,
        postgres_password,
        new_database_name,
    )


def add_user(
    fullname=None,
    email=None,
    hashed_password=None,
    hostname=None,
    postgres_username="postgres",
    postgres_password=None,
    postgres_database="molar_main",
):
    connection = sql_utils.create_connection(
        postgres_username, postgres_password, hostname, postgres_database
    )
    query = text(
        (
            'insert into "user".user '
            '("full_name", "email", "hashed_password", '
            '"is_superuser", "is_active", "created_on") '
            "values "
            "( :fullname, :email, :hashed_password, "
            "true, true, now()::timestamp )"
        )
    )
    connection.execute(
        query,
        {"fullname": fullname, "email": email, "hashed_password": hashed_password},
    )
    connection.close()


def create_database(
    alembic_config,
    hostname,
    postgres_username,
    postgres_password,
    new_database_name,
    revisions,
):
    connection = sql_utils.create_connection(
        postgres_username, postgres_password, hostname, "postgres"
    )
    connection.execution_options(isolation_level="AUTOCOMMIT").execute(
        f"create database {new_database_name}"
    )
    connection.close()
    connection = sql_utils.create_connection(
        postgres_username, postgres_password, hostname, new_database_name
    )

    alembic_config.set_main_option(
        "sqlalchemy.url",
        PostgresDsn.build(
            scheme="postgresql",
            user=postgres_username,
            password=postgres_password,
            host=hostname,
            path=f"/{new_database_name}",
        ),
    )
    command.upgrade(alembic_config, revisions)
    connection.close()


def drop_database(hostname, postgres_username, postgres_password, database):
    connection = sql_utils.create_connection(
        postgres_username, postgres_password, hostname, "postgres"
    )
    connection.execution_options(isolation_level="AUTOCOMMIT").execute(
        f"drop database {database} with (force)"
    )
    connection.close()
