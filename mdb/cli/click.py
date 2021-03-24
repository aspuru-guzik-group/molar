from rich import traceback
from rich.console import Console

import click


class CustomClickCommand(click.Command):
    _original_args = None

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except Exception as exc:
            handle_exception(ctx.obj["console"], ctx.info_name, exc)


def handle_exception(console, info_name, exception):
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
