from datetime import datetime

from alembic import command
from pydantic import PostgresDsn

from . import sql_utils


def install_molar_database(
    alembic_config,
    hostname,
    postgres_username,
    postgres_password,
    new_database_name,
    superuser_email,
    superuser_hashed_password,
    revisions,
):
    if "fb3f43ec8aaa" not in revisions:
        revisions.insert(0, "fb3f43ec8aaa")
    if "c59a26437bf4" not in revisions:
        revisions.insert(0, "c59a26437bf4")
    create_database(
        alembic_config,
        hostname,
        postgres_username,
        postgres_password,
        new_database_name,
        revisions,
    )
    add_user(
        superuser_email,
        superuser_hashed_password,
        hostname,
        postgres_username,
        postgres_password,
        new_database_name,
    )


def add_user(
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
    connection.execute(
        (
            'insert into "user".user '
            '       ("email", '
            '        "hashed_password", '
            '        "is_superuser", '
            '        "is_active" , '
            '        "created_on") '
            "values "
            f"('{email}', "
            f" '{hashed_password}',"
            " true,"
            " true,"
            f" '{datetime.utcnow()}'::TIMESTAMP);"
        )
    )


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
    for revision in revisions:
        command.upgrade(alembic_config, revision)
    connection.close()


def drop_database(hostname, postgres_username, postgres_password, database):
    connection = sql_utils.create_connection(
        postgres_username, postgres_password, hostname, "postgres"
    )
    connection.execution_options(isolation_level="AUTOCOMMIT").execute(
        f"drop database {database} with (force)"
    )
    connection.close()
