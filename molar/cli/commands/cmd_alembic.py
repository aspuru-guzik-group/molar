# external
from alembic import command
import click
from rich.prompt import Confirm

from .. import alembic_utils
from ..alembic_utils import get_alembic_config, GLOBAL_VERSION_PATH
from ..cli_utils import CustomClickCommand


@click.group(help="Alembic wrapper")
@click.pass_context
def alembic(ctx):
    ctx.obj["alembic_config"] = get_alembic_config(ctx)
    pass


@alembic.command(cls=CustomClickCommand)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def branches(ctx, verbose):
    command.branches(ctx.obj["alembic_config"], verbose)


@alembic.command(cls=CustomClickCommand)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def current(ctx, verbose):
    command.current(ctx.obj["alembic_config"], verbose)


@alembic.command(cls=CustomClickCommand)
@click.argument("revision", nargs=1, type=str, required=True)
@click.option("-s", "--sql", is_flag=True)
@click.option("-t", "--tag", type=str)
@click.pass_context
def downgrade(ctx, revision, sql=False, tag=None):
    command.downgrade(ctx.obj["alembic_config"], revision, sql, tag)


@alembic.command(cls=CustomClickCommand)
@click.argument("revision", nargs=1, type=str, required=True)
@click.pass_context
def edit(ctx, revision):
    command.edit(ctx.obj["alembic_config"], revision)


@alembic.command(cls=CustomClickCommand)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-d", "--resolve-dependancies", is_flag=True)
@click.pass_context
def heads(ctx, verbose=False, resolve_dependancies=False):
    command.heads(ctx.obj["alembic_config"], verbose, resolve_dependancies)


@alembic.command(cls=CustomClickCommand)
@click.option("-r", "--revision-range", type=str)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-i", "--indicate-current", is_flag=True)
@click.pass_context
def history(ctx, revision_range, verbose, indicate_current):
    command.history(
        ctx.obj["alembic_config"], revision_range, verbose, indicate_current
    )


@alembic.command(cls=CustomClickCommand)
@click.argument("revisions", nargs=-1, type=str)
@click.option("-m", "--message", type=str)
@click.option("--branch-label", type=str, default=None)
@click.option("--revision-id", type=str, default=None)
@click.pass_context
def merge(ctx, revisions, message, branch_label, revision_id):
    if not verify_data_dir(ctx):
        return

    version_path = ctx.obj["data_dir"].resolve() / "migrations"

    alembic_utils.merge(
        ctx.obj["alembic_config"],
        revisions,
        message,
        branch_label,
        version_path,
        revision_id,
    )


@alembic.command(cls=CustomClickCommand)
@click.option("-m", "--message", type=str)
@click.option("-a", "--autogenerate", is_flag=True)
@click.option("--sql", is_flag=True)
@click.option("--head", type=str, default="head")
@click.option("--splice", is_flag=True)
@click.option("--branch-label", type=str, default=None)
@click.option("--revision-id", type=str, default=None)
@click.option("--depends-on", type=str, default=None)
@click.pass_context
def revision(
    ctx,
    message,
    head,
    splice,
    branch_label,
    revision_id,
    autogenerate=True,
    sql=False,
    depends_on=None,
):
    if not verify_data_dir(ctx):
        return

    version_path = ctx.obj["data_dir"].resolve() / "migrations"

    command.revision(
        ctx.obj["alembic_config"],
        message,
        autogenerate,
        sql,
        head,
        splice,
        branch_label,
        version_path,
        revision_id,
        depends_on,
    )


def verify_data_dir(ctx):
    console = ctx.obj["console"]
    if "data_dir" not in ctx.obj.keys() or ctx.obj["data_dir"] is None:
        console.log(
            (
                "[bold red]No data-dir has been specified![/bold red]\n"
                "This means the migration will be directly added to the repository.\n"
                "This is usually alright if you are developping Molar, "
                "otherwise you should consider setting a data-directory.\n"
            )
        )
        return Confirm.ask("Are you sure you want to proceed?")
    return True


@alembic.command(cls=CustomClickCommand)
@click.argument("revision", type=str)
@click.pass_context
def show(ctx, revision):
    command.show(ctx.obj["alembic_config"], revision)


@alembic.command(cls=CustomClickCommand)
@click.argument("revision", nargs=1, type=str)
@click.option("-s", "--sql", is_flag=True)
@click.option("-t", "--tag", type=str)
@click.pass_context
def upgrade(ctx, revision, sql=False, tag=None):
    command.upgrade(ctx.obj["alembic_config"], revision, sql, tag)
