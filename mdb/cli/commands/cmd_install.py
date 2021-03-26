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


@install.command(cls=CustomClickCommand, help="Spin up a database locally with docker")
@click.pass_context
def local(ctx):
    # Spin up with docker
    client = docker.from_env()
    client.containers.run("tgaudin/postgresql-pgtap", detach=True)
    pass


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
    console = ctx.obj["console"]
    if getattr(ctx.obj["client_config"], "user_dir", None) is None:
        console.log(
            "[red bold]You must specify a user-dir for this operation![/red bold]"
        )
        return

    with console.status(f"[bold green]Creating the database[/bold green]") as status:
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
    console.log("Molar :tooth: is installed!")


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


# def install_molar_on_postgresql(
#     console,
#     alembic_conf,
#     user,
#     password,
#     hostname,
#     new_database_name,
#     admin_username,
#     admin_password,
#     basic_username,
#     basic_password,
#     ro_username,
#     ro_password,
# ):
#     with console.status("[bold green]Installing Molar...") as status:
#         connection = sql_utils.create_connection(user, password, hostname, "postgres")
#         connection.execute_options(isolation_level="AUTOCOMMIT").execute(
#             f"create database {new_database_name}"
#         )
#         connection.close()
#         console.log("Database created")
#         command.upgrade(alembic_conf, "head")
#         console.log("Database structure installed")
#         sql_utils.create_user(connection, admin_username, admin_password)
#         sql_utils.create_user(connection, basic_username, basic_password)
#         sql_utils.transfer_ownership(admin)
#         sql_utils.grant_access_right(user)
#         console.log("Admin and basic user created")
