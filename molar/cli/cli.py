import logging
import os
import pathlib
from pathlib import Path

import click
from rich.console import Console

from ..config import ClientConfig
from .commands.cmd_alembic import alembic
from .commands.cmd_install import install


@click.group()
@click.option("-u", "--username", default=None)
@click.option("-p", "--password", default=None)
@click.option("-h", "--hostname", default=None)
@click.option("-d", "--database-name", default=None)
@click.option("--user-dir", type=Path, default=None)
@click.option("--log-level", type=str, default="INFO")
@click.pass_context
def cli(ctx, username, password, hostname, database_name, user_dir, log_level):
    ctx.ensure_object(dict)

    ctx.obj["console"] = Console()
    if user_dir is not None and not user_dir.exists():
        ctx.obj["console"].log(
            (
                f"The specified user_dir does not exists {user_dir}!\n"
                f"Creating {user_dir}."
            )
        )
        os.mkdir(user_dir)

    logging.basicConfig(level=log_level)

    config = ClientConfig(
        username=username,
        password=password,
        hostname=hostname,
        database=database_name,
        user_dir=user_dir,
        log_level=log_level,
    )
    ctx.obj["client_config"] = config


cli.add_command(alembic)
cli.add_command(install)
