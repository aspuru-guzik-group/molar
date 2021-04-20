import configparser
import random
import string
from distutils.spawn import find_executable
from time import sleep
from typing import List

import click
import docker
from alembic import command
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ...registry import REGISTRIES
from .. import alembic_utils, sql_utils

# from .. import sql_utils
from ..cli_utils import CustomClickCommand


@click.group(help="Molar Installation")
@click.pass_context
def install(ctx):
    ctx.obj["alembic_config"] = alembic_utils.get_alembic_config(
        ctx.obj["client_config"]
    )
    pass


# TODO: global install of config file?
# TODO: installing without asking anything


@install.command(cls=CustomClickCommand, help="Spin up a database locally with docker")
@click.option(
    "--postgres-password", prompt="Chose a password for postgres user", hide_input=True
)
@click.pass_context
def local(ctx, postgres_password):
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
        container = client.containers.get("molar-pgsql")
    except docker.errors.NotFound:
        _start_docker_container(ctx, client, postgres_password)
        container = client.containers.get("molar-pgsql")

    if container.status != "running":
        container.start()

    with console.status("Starting database..."):
        while (
            not "database system is ready to accept connections"
            in container.logs().decode()
        ):
            sleep(1)

    _install_molar(ctx, "localhost", "postgres", postgres_password, None)


def _generate_password(password_length=16):
    characters_choice = string.ascii_letters + string.digits
    return "".join(random.sample(characters_choice, password_length))


def _install_molar(
    ctx,
    hostname=None,
    postgres_username="postgres",
    postgres_password=None,
    new_database_name=None,
):
    console = ctx.obj["console"]
    if hostname is None:
        hostname = Prompt.ask(
            "What is the hostname of the postgres server to install Molar :tooth: on?"
        )
    if postgres_password is None:
        postgres_password = Prompt.ask("Postgres password?", password=True)
    if new_database_name is None:
        new_database_name = Prompt.ask("Name of the new database?")

    admin_username = f"{new_database_name}_admin"
    admin_password = _generate_password()
    user_username = new_database_name
    user_password = _generate_password()
    user_dir = ctx.obj["client_config"].user_dir

    with console.status("Installing Molar :tooth:..."):
        console.log("Creating database")
        _create_database(
            ctx,
            hostname,
            postgres_username,
            postgres_password,
            new_database_name,
            False,
        )
        console.log("Creating admin user")
        connection = sql_utils.create_connection(
            postgres_username, postgres_password, hostname, new_database_name
        )
        sql_utils.create_user(connection, admin_username, admin_password)
        sql_utils.transfer_ownership(connection, new_database_name, admin_username)
        console.log("Creating normal user")
        sql_utils.create_user(connection, user_username, user_password)
        sql_utils.grant_access_right(connection, user_username)
        console.log("Writing config files")
        _write_default_config_file(
            user_dir / "molar_admin.conf",
            hostname,
            new_database_name,
            admin_username,
            admin_password,
        )
        _write_default_config_file(
            user_dir / "molar_user.conf",
            hostname,
            new_database_name,
            user_username,
            user_password,
        )
        console.log("Molar :tooth: is insalled!")


def _write_default_config_file(path, hostname, database, username, password):
    config = configparser.ConfigParser()
    config[f"{hostname}/{database}"] = {
        "hostname": hostname,
        "database": database,
        "username": username,
        "password": password,
        "return_pandas_dataframe": True,
        "log_level": "INFO",
    }
    with open(path, "w") as f:
        config.write(f)


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


def _start_docker_container(ctx, client: docker.DockerClient, postgres_password=None):
    if postgres_password is None:
        Prompt.ask("Enter a password for postgres user:", password=True)
    client.containers.run(
        "tgaudin/postgresql-pgtap",
        name="molar-pgsql",
        environment={"POSTGRES_PASSWORD": postgres_password},
        detach=True,
        ports={"5432/tcp": 5432},
        volumes={
            "/var/lib/postgresql/data": {
                "bind": str((ctx.obj["client_config"].user_dir / "data").resolve()),
                "mode": "rw",
            }
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

    version_path = ctx.obj["client_config"].user_dir / "migrations"
    revisions = choose_structure(ctx.obj["console"], advanced)
    alembic_config = ctx.obj["alembic_config"]
    alembic_config.set_main_option(
        "sqlalchemy.url",
        (
            f"postgresql://{postgres_username}:{postgres_password}"
            f"@{hostname}/{new_database_name}"
        ),
    )
    alembic_utils.merge(
        ctx.obj["alembic_config"],
        revisions,
        "Merging for installation",
        version_path=version_path,
        branch_labels="install",
    )
    command.upgrade(alembic_config, "install@head")
    connection.close()


def choose_structure(console: Console, interactive: bool) -> List[str]:
    # TODO: improve this message
    if (
        not Confirm.ask("Do you want to choose the database structure?")
        and not interactive
    ):
        default: List[str] = []
        for name, details in REGISTRIES["alembic_revision"].items():
            if not details["default"]:
                continue

            default.append(name + "@head")
            for option in details["options"]:
                if option["default"]:
                    default.append(option["branch_label"] + "@head")
        return default

    branches: List[str] = []
    for name, details in REGISTRIES["alembic_revision"].items():
        out = Confirm.ask(f"Do you want to install {name} ({details['help']}) ?")
        if not out:
            continue

        branches.append(name + "@head")
        console.log(f"[bold]Options for {name}[/bold]")
        for option in details["options"]:
            console.log(f" - {option['branch_label']}")
            console.log(f"{option['help']}")
            out = Confirm.ask(f"Do you want to install this option for {name}?")
            if not out:
                continue
            branches.append(option["branch_label"] + "@head")
    return branches
