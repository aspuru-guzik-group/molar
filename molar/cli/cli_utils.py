# std
from pathlib import Path
from typing import Any, List, Optional, Union

# external
import click
from dotenv import dotenv_values
from pydantic import PostgresDsn
from rich import traceback
from rich.console import Console


class CustomClickCommand(click.Command):
    _original_args = None

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except Exception as exc:
            handle_exception(ctx.obj["console"], ctx.info_name)


def handle_exception(console: Console, info_name: str):
    traceback.install()
    console.print_exception()
    console.log(
        f"[bold red]Something went wrong "
        f"with the following commmand: {info_name}[/bold red]"
    )
    console.log(
        (
            "If you can't resolve this issue yourself, "
            "please open an issue on our GitHub repo"
        )
    )
    exit(1)


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

    if not env_file.exists() and data_dir is None:
        console.log(
            ".env file not found and no data_dir provided. Please specify --data-dir or --env-file"
        )
        exit(1)

    ctx.obj["data_dir"] = data_dir
    ctx.obj["env_file"] = env_file
    config = dotenv_values(env_file)
    ctx.obj["env"] = config
    ctx.obj["sql_url"] = PostgresDsn.build(
        scheme="postgresql",
        host=config["POSTGRES_SERVER"],
        user=config["POSTGRES_USER"],
        password=config["POSTGRES_PASSWORD"],
        path=f"/{database or ''}",
    )
