# std
from typing import Dict

# external
from pydantic import PostgresDsn
import sqlalchemy

from . import query
from ..core.config import settings
from .database_handler import DatabaseHandler

DATABASE_REGISTRY: Dict[str, DatabaseHandler] = {}


DATABASE_REGISTRY["main"] = DatabaseHandler(
    settings.SQLALCHEMY_DATABASE_URI, schemas=["public", "user"]
)


def __getattr__(database_name: str):
    if database_name in DATABASE_REGISTRY.keys():
        return DATABASE_REGISTRY[database_name]

    try:
        db_handler = DatabaseHandler(
            PostgresDsn.build(
                scheme="postgresql",
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_SERVER,
                path=f"/{database_name}",
            )
        )
    except sqlalchemy.exc.OperationalError:
        return None
    DATABASE_REGISTRY[database_name] = db_handler
    return db_handler


def close_database(database_name: str):
    if database_name not in DATABASE_REGISTRY.keys():
        return

    db = DATABASE_REGISTRY[database_name]
    db.close()
    del DATABASE_REGISTRY[database_name]
