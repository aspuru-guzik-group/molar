from pathlib import Path

import click
from rich.console import Console

from ..config import ClientConfig
from .commands.cmd_alembic import alembic
from .commands.cmd_install import install


@click.group()
@click.option("-u", "--username")
@click.option("-p", "--password")
@click.option("-h", "--hostname")
@click.option("-d", "--database-name")
@click.option("--user-dir", type=Path)
@click.pass_context
def cli(ctx, username, password, hostname, database_name, user_dir=None):
    ctx.ensure_object(dict)

    ctx.obj["console"] = Console()
    if user_dir is not None and not user_dir.exists():
        ctx.obj["console"].log(
            (
                f"The specified user_dir does not exists {user_dir}!\n"
                "Please specify a valid user_dir."
            )
        )
        exit(1)
    
    config = ClientConfig(
        username=username,
        password=password,
        hostname=hostname,
        database=database_name,
        user_dir=user_dir,
    )
    ctx.obj["client_config"] = config


cli.add_command(alembic)
cli.add_command(install)
