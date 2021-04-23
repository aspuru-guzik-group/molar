import pkg_resources
from alembic import util
from alembic.config import Config
from alembic.script import ScriptDirectory

from ..config import ClientConfig

GLOBAL_VERSION_PATH = pkg_resources.resource_filename("molar", "migrations/versions")


def get_alembic_config(cfg: ClientConfig):
    alembic_config = Config()
    version_locations = GLOBAL_VERSION_PATH
    if cfg.user_dir:
        version_locations = version_locations + " " + str(cfg.user_dir / "migrations")
    alembic_config.set_main_option("version_locations", version_locations)
    alembic_config.set_main_option("script_location", "molar:migrations")
    alembic_config.set_main_option("sqlalchemy.url", cfg.sql_url)
    return alembic_config


def merge(
    config, revisions, message=None, branch_labels=None, version_path=None, rev_id=None
):
    """
    Merge allowing to specify a version_path
    """
    script = ScriptDirectory.from_config(config)
    return script.generate_revision(
        rev_id or util.rev_id(),
        message,
        refresh=True,
        head=revisions,
        branch_labels=branch_labels,
        version_path=version_path,
        config=config,
    )
