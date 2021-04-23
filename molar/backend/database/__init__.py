from typing import Dict

import sqlalchemy
from pydantic import PostgresDsn

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
