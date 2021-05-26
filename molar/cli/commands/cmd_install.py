import configparser
import random
import string
from datetime import datetime
from distutils.spawn import find_executable
from time import sleep
from typing import List, Optional

import click
import docker
from alembic import command
from molar import sql_utils
from passlib.context import CryptContext
from rich.console import Console
from rich.prompt import Confirm, Prompt
from time import sleep
from .. import alembic_utils

# from .. import sql_utils
from ..cli_utils import CustomClickCommand

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@click.group(help="Molar Installation")
@click.pass_context
def install(ctx):
    ctx.obj["alembic_config"] = alembic_utils.get_alembic_config(
        ctx.obj["client_config"]
    )
    pass


@install.command(cls=CustomClickCommand, help="Spin up Molar locally with docker")
@click.option(
    "--postgres-password", prompt="Chose a password for postgres user", hide_input=True
)
@click.option(
    "--container-name",
    type=str,
    default="molar-pgsql",
    help="Name of the docker container (default: molar-pgsql)",
)
@click.option("--superuser-name", type=str, default=None)
@click.option("--superuser-email", type=str, default=None)
@click.option("--superuser-password", type=str, default=None)
@click.pass_context
def local(
    ctx,
    postgres_password,
    container_name,
    superuser_name,
    superuser_email,
    superuser_password,
):
    console = ctx.obj["console"]
    if not find_executable("docker"):
        console.log(
            (
                "[red bold]Docker is not installed[/], "
                "please install it from https://docker.com"
            )
        )
        return
    _verify_user_dir(ctx)
    client = docker.DockerClient()

    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        _start_docker_container(ctx, client, container_name, postgres_password)
        container = client.containers.get(container_name)

    if container.status != "running":
        container.start()

    with console.status("Starting database..."):
        while (
            not "database system is ready to accept connections"
            in container.logs().decode()
        ):
            sleep(1)

    sleep(2)
    _install_molar(ctx, "localhost", "postgres", postgres_password)

    console.log("Creating the first user!")
    if superuser_name is None:
        superuser_email = Prompt.ask("Name")
    if superuser_email is None:
        superuser_email = Prompt.ask("Email")
    if superuser_password is None:
        superuser_password = Prompt.ask("Password", password=True)

    _add_user(
        user_name=superuser_name,
        email=superuser_email,
        password=superuser_password,
        hostname="localhost",
        postgres_username="postgres",
        postgres_password=postgres_password,
        postgres_database="molar_main",
    )

    console.log("Molar :tooth: is insalled!")


@install.command(cls=CustomClickCommand, help="Set up remote postgres database")
@click.option("--hostname", type=str)
@click.option("--postgres-username")
@click.option("--postgres-password")
@click.option("--superuser-email", type=str, default=None)
@click.option("--superuser-password", type=str, default=None)
@click.pass_context
def remote(
    ctx,
    hostname,
    postgres_username,
    postgres_password,
    superuser_email,
    superuser_password,
):
    console = ctx.obj["console"]
    _install_molar(ctx, hostname, postgres_username, postgres_password)

    console.log("Creating the first user!")
    if superuser_email is None:
        superuser_email = Prompt.ask("Email")
    if superuser_password is None:
        superuser_password = Prompt.ask("Password", password=True)

    _add_user(
        email=superuser_email,
        password=superuser_password,
        hostname=hostname,
        postgres_username="postgres",
        postgres_password=postgres_password,
        postgres_database="molar_main",
    )

    console.log(f"Molar :tooth: is insalled on {hostname}!")


def _install_molar(
    ctx,
    hostname=None,
    postgres_username="postgres",
    postgres_password=None,
):
    console = ctx.obj["console"]
    if hostname is None:
        hostname = Prompt.ask(
            "What is the hostname of the postgres server to install Molar :tooth: on?"
        )
    if postgres_password is None:
        postgres_password = Prompt.ask("Postgres password?", password=True)

    with console.status("Installing Molar :tooth:..."):
        console.log("Creating database")
        _create_database(
            ctx,
            hostname,
            postgres_username,
            postgres_password,
            "molar_main",
            False,
        )


def _add_user(
    user_name=None,
    email=None,
    password=None,
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
            '       ("full_name", '
            '        "email", '
            '        "hashed_password", '
            '        "is_superuser", '
            '        "is_active" , '
            '        "created_on") '
            "values "
            f"('{user_name}',"
            f"'{email}', "
            f" '{pwd_context.hash(password)}',"
            " true,"
            " true,"
            f" '{datetime.utcnow()}');"
        )
    )


@install.command(
    cls=CustomClickCommand, help="Create a new database on a postgresql server"
)
@click.option("--hostname", type=str, prompt="Database hostname")
@click.option("--postgres-username", type=str, default="postgres")
@click.option(
    "--postgres-password", type=str, prompt="Postgres password", hide_input=True
)
@click.option("--new-database-name", type=str, prompt="Name of the new database")
@click.option("--advanced", is_flag=True)
@click.pass_context
def create_database(
    ctx, hostname, postgres_username, postgres_password, new_database_name, advanced
):
    _verify_user_dir(ctx)
    _create_database(
        ctx, hostname, postgres_username, postgres_password, new_database_name, advanced
    )


def _start_docker_container(
    ctx, client: docker.DockerClient, container_name: str, postgres_password=None
):
    if postgres_password is None:
        Prompt.ask("Enter a password for postgres user:", password=True)
    client.containers.run(
        "tgaudin/postgresql-pgtap",
        name=container_name,
        environment={
            "ALEMBIC_USER_DIR": "/var/lib/molar/migrations",
            "POSTGRES_PASSWORD": postgres_password,
        },
        detach=True,
        ports={"5432/tcp": 5432},
        volumes={
            "/var/lib/postgresql/data": {
                "bind": str((ctx.obj["client_config"].user_dir / "data").resolve()),
                "mode": "rw",
            },
            "/var/lib/molar/migrations": {
                "bind": str(
                    (ctx.obj["client_config"].user_dir / "migrations").resolve()
                ),
                "mode": "rw",
            },
        },
    )


def _verify_user_dir(ctx):
    console = ctx.obj["console"]
    if getattr(ctx.obj["client_config"], "user_dir", None) is None:
        console.log(
            "[red bold]You must specify a user-dir for this operation![/red bold]"
        )
        exit(1)


def _create_database(
    ctx, hostname, postgres_username, postgres_password, new_database_name, advanced
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

    alembic_config = ctx.obj["alembic_config"]
    alembic_config.set_main_option(
        "sqlalchemy.url",
        (
            f"postgresql://{postgres_username}:{postgres_password}"
            f"@{hostname}/{new_database_name}"
        ),
    )
    command.upgrade(alembic_config, "molar-main@head")
    connection.close()
