# external
from alembic.config import Config
from alembic.script import ScriptDirectory
import pkg_resources
from pydantic import PostgresDsn

from .core.config import settings

GLOBAL_VERSION_PATH = pkg_resources.resource_filename("molar", "migrations/versions")


def get_alembic_config(database: str = ""):
    sqlalchemy_url = PostgresDsn.build(
        scheme="postgresql",
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        path=f"/{database or ''}",
    )

    alembic_config = Config()

    version_locations = GLOBAL_VERSION_PATH
    if settings.ALEMBIC_USER_DIR is not None:
        version_locations = (
            version_locations + " " + str(settings.ALEMBIC_USER_DIR.resolve())
        )
    alembic_config.set_main_option("version_locations", version_locations)
    alembic_config.set_main_option("script_location", "molar:migrations")
    alembic_config.set_main_option("sqlalchemy.url", sqlalchemy_url)
    return alembic_config


def get_revisions(config: Config):
    script = ScriptDirectory.from_config(config)
    revs = script.get_revisions(script.get_heads())
    return revs
