# std
from datetime import datetime
from distutils.spawn import find_executable
import os
from pathlib import Path
import secrets
import shutil
import stat
import subprocess
from time import sleep
from typing import List, Optional

# external
from alembic import command
import click
from dotenv import dotenv_values
from passlib.context import CryptContext
import pkg_resources
from python_on_whales import docker
from python_on_whales.utils import DockerException
from rich.console import Console
from rich.prompt import Confirm, Prompt

# molar
from molar import sql_utils

from .. import alembic_utils
from ..cli_utils import CustomClickCommand

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@click.group(help="Molar Installation")
@click.pass_context
def install(ctx):
    pass


def config_env_vars(
    console: Console,
    data_dir: Path,
    *,
    postgres_server: Optional[str] = None,
    postgres_user: Optional[str] = None,
    postgres_password: Optional[str] = None,
    server_host: Optional[str] = None,
    emails_enabled: Optional[bool] = None,
    smtp_tls: Optional[bool] = None,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    emails_from_email: Optional[str] = None,
    emails_from_name: Optional[str] = None,
    backend_port: Optional[int] = None,
    backend_num_workers: Optional[int] = None,
):
    console.log("[blue bold]Setting up backend environment..")
    if (data_dir / ".env").exists():
        if Confirm.ask(
            (
                f"[red bold]A .env file already exists in {str(data_dir.resolve())}.\n"
                "Do you want to use it?"
            )
        ):
            return dotenv_values((data_dir / ".env"))

    if postgres_server is None:
        postgres_server = Prompt.ask("PostgreSQL server hostname", default="localhost")
    if postgres_user is None:
        postgres_user = Prompt.ask("PostgreSQL user", default="postgres")
    if postgres_password is None:
        postgres_password = Prompt.ask(f"Password for Postgres admin", password=True)
    if server_host is None:
        server_host = Prompt.ask(f"Server url", default="http://localhost")
    if emails_enabled is None:
        emails_enabled = Confirm.ask("Allow the backend to send email?")
    if emails_enabled:
        if smtp_host is None:
            smtp_host = Prompt.ask("SMTP server")
        if smtp_port is None:
            smtp_port = Prompt.ask("SMTP Port", default=25)
        if smtp_user is None:
            smtp_user = Prompt.ask("SMTP user")
        if smtp_password is None:
            smtp_password = Prompt.ask("SMTP password", password=True)
        if smtp_tls is None:
            smtp_tls = Confirm.ask("Use TLS to connect to the SMTP server?")
        if emails_from_email is None:
            emails_from_email = Prompt.ask("Email address of the bakcend")
        if emails_from_name is None:
            emails_from_name = Prompt.ask("Email name of the backend")
    if backend_port is None:
        backend_port = Prompt.ask("Backend port", default="8000")
    if backend_num_workers is None:
        backend_num_workers = Prompt.ask(
            "Number of workers for the backend", default="2"
        )

    dotenv_file = (data_dir / ".env").resolve()
    with open(dotenv_file, "w") as f:
        print(f"DATA_DIR={data_dir.resolve()}", file=f)
        print(f"POSTGRES_SERVER={postgres_server}", file=f)
        print(f"POSTGRES_USER={postgres_user}", file=f)
        print(f"POSTGRES_PASSWORD={postgres_password}", file=f)
        print(f"SERVER_HOST={server_host}", file=f)
        print(f"EMAILS_ENABLED={'true' if emails_enabled else 'false'}", file=f)
        print(f"SMTP_TLS={'true' if smtp_tls else 'false'}", file=f)
        print(f"SMTP_HOST={smtp_host or ''}", file=f)
        print(f"SMTP_PORT={smtp_port or 25}", file=f)
        print(f"SMTP_USER={smtp_user or ''}", file=f)
        print(f"SMTP_PASSWORD={smtp_password or ''}", file=f)
        print(f"EMAILS_FROM_EMAIL={emails_from_email or 'noreply@molar.local'}", file=f)
        print(f"EMAILS_FROM_NAME={emails_from_name or ''}", file=f)
        print(f"BACKEND_PORT={backend_port}", file=f)
        print(f"BACKEND_NUM_WORKERS={backend_num_workers}", file=f)
        print(f"ALEMBIC_USER_DIR=/alembic", file=f)
        print(f"SECRET_KEY={secrets.token_urlsafe(32)}", file=f)
    os.chmod(dotenv_file, stat.S_IREAD)
    return locals()


@install.command(
    cls=CustomClickCommand, help="Install Molar locally with docker compose"
)
@click.pass_context
def local(ctx):
    def _compose_status_healthy():
        try:
            status = docker.compose.ps()[0].state.health.status == "healthy"
        except:
            out = subprocess.check_output(
                "docker-compose ps | grep postgres", shell=True
            )
            status = "healthy" in str(out)
        return status

    console = ctx.obj["console"]
    if not find_executable("docker"):
        console.log(
            (
                "[red bold]Docker is not installed[/], "
                "please install it from https://docker.com"
            )
        )
        return

    _verify_data_dir(ctx)
    data_dir = ctx.obj["data_dir"]

    config = config_env_vars(
        console,
        data_dir,
        postgres_server="postgres",
        postgres_user="postgres",
    )
    molar_docker_compose = pkg_resources.resource_filename(
        "molar", "docker/docker-compose.yml"
    )
    local_docker_compose = data_dir / "docker-compose.yml"
    shutil.copyfile(molar_docker_compose, local_docker_compose)
    os.chdir(data_dir)
    with console.status("Setting up PostgreSQL (this can take a few minutes)..."):
        try:
            docker.compose.up(services=["postgres"], detach=True)
        except DockerException:
            # docker compose up --detach doesn't work with some
            # version of docker
            subprocess.call(["docker-compose", "up", "-d", "postgres"])
        while not _compose_status_healthy():
            sleep(1)
    sleep(2)

    console.log("Installing Molar...")
    _install_molar(ctx, "localhost", "postgres", config["postgres_password"])

    console.log("[bold blue]Creating the first superuser[/bold blue]")
    superuser_name = Prompt.ask("Full name")
    superuser_email = Prompt.ask("Email")
    superuser_password = Prompt.ask("Password", password=True)

    _add_user(
        user_name=superuser_name,
        email=superuser_email,
        password=superuser_password,
        hostname="localhost",
        postgres_username="postgres",
        postgres_password=config["postgres_password"],
        postgres_database="molar_main",
    )

    console.log("Molar :tooth: is insalled!")
    if Confirm.ask("Do you want to start it now?"):
        try:
            docker.compose.up(detach=True)
        except DockerException:
            subprocess.call("docker-compose up -d", shell=True)
    else:
        try:
            docker.compose.down()
        except DockerException:
            subprocess.call("docker-compose down", shell=True)


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


def _verify_data_dir(ctx):
    console = ctx.obj["console"]
    data_dir = ctx.obj["data_dir"]
    if data_dir is None:
        console.log("[blue bold]No data-dir where specified![/blue bold]")
        data_dir = Path(
            Prompt.ask(
                "Where do you want to install Molar :tooth:", default="./molar_data_dir"
            )
        )

    if not data_dir.exists():
        data_dir.mkdir()

    alembic_dir = data_dir / "migrations"
    if not alembic_dir.exists():
        alembic_dir.mkdir()

    postgres_dir = data_dir / "postgres"
    if not postgres_dir.exists():
        postgres_dir.mkdir()
    ctx.obj["data_dir"] = data_dir.resolve()


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

    alembic_config = alembic_utils.get_alembic_config(ctx, database="molar_main")
    alembic_config.set_main_option(
        "sqlalchemy.url",
        (
            f"postgresql://{postgres_username}:{postgres_password}"
            f"@{hostname}/{new_database_name}"
        ),
    )
    command.upgrade(alembic_config, "molar-main@head")
    connection.close()
