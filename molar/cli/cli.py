# std
import logging
import os
import pathlib
from pathlib import Path
from typing import Optional

# external
import click
from dotenv import dotenv_values
from pydantic import PostgresDsn
from rich.console import Console

from .commands.cmd_alembic import alembic
from .commands.cmd_install import install


@click.group()
@click.option(
    "--data-dir",
    type=Path,
    default=None,
    help="Molar data directory (where it is installed)",
)
@click.option(
    "--env-file",
    type=Path,
    default=None,
    help="Molar .env file (usually data_dir/.env)",
)
@click.option("--log-level", type=str, default="INFO")
@click.option(
    "--database",
    type=str,
    default=None,
    help="Database name (used for some alembic operations)",
)
@click.pass_context
def cli(ctx, data_dir, env_file, log_level, database):
    ctx.ensure_object(dict)
    ctx.obj["console"] = Console()
    ctx.obj["data_dir"] = data_dir
    ctx.obj["env_file"] = env_file
    ctx.obj["database"] = database


cli.add_command(alembic)
cli.add_command(install)
