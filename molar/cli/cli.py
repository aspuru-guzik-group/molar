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


def load_config(
    ctx,
    database: Optional[str],
    data_dir: Optional[Path] = None,
    env_file: Optional[Path] = None,
):
    console = ctx.obj["console"]
    if data_dir is None and ctx.obj["data_dir"] is None:
        data_dir = Path("./")
    else:
        data_dir = ctx.obj["data_dir"]
    if env_file is None and ctx.obj["env_file"] is None:
        env_file = data_dir / ".env"
    else:
        env_file = ctx.obj["env_file"]

    if database is None and ctx.obj["database"] is not None:
        database = ctx.obj["database"]

    if not env_file.exists():
        raise ValueError(
            ".env file not found. Please specifiy --data-dir or --env-file"
        )

    config = dotenv_values(env_file)
    ctx.obj["env"] = config
    ctx.obj["sql_url"] = PostgresDsn.build(
        host=config["POSTGRES_SERVER"],
        user=config["POSTGRES_USER"],
        password=config["POSTGRES_PASSWORD"],
        path=f"/{database or ''}",
    )


cli.add_command(alembic)
cli.add_command(install)
