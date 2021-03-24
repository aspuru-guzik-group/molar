import click
import pkg_resources
from alembic import command
from alembic.config import Config

from ...config import ClientConfig
from ..click import CustomClickCommand

GLOBAL_VERSION_PATH = pkg_resources.resource_filename(
    *"mdb:migrations/versions".split(":")
)


def get_alembic_config(cfg: ClientConfig):
    alembic_config = Config()
    version_locations = GLOBAL_VERSION_PATH
    if cfg.user_dir:
        version_locations = version_locations + " " + str(cfg.user_dir / "migrations")
    alembic_config.set_main_option("version_locations", version_locations)
    alembic_config.set_main_option("script_location", "mdb:migrations")
    alembic_config.set_main_option("sqlalchemy.url", cfg.sql_url)
    return alembic_config


@click.group(help="Alembic wrapper")
@click.pass_context
def alembic(ctx):
    ctx.obj["alembic_config"] = get_alembic_config(ctx.obj["client_config"])
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
    console = ctx.obj["console"]
    if getattr(ctx.obj["client_config"], "user_dir", None) is None:
        console.log(
            (
                "[bold red]No user-dir has been specified![/bold red]\n"
                "This means the migration will be directly added to the repository.\n"
                "This is usually alright if you are developping mdb, "
                "otherwise you should consider setting a user-directory.\n"
            )
        )
        while True:
            out = console.input("Are you sure you want to proceed? (y/N)")
            if out == "" or out.lower() == "n":
                return
            elif out.lower() == "y":
                break

    version_path = (
        GLOBAL_VERSION_PATH
        if ctx.obj["client_config"].user_dir is None
        else ctx.obj["client_config"].user_dir / "migrations"
    )
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
