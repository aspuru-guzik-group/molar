# std
from typing import Generator, List
import warnings

# external
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from ..crud import CRUDInterface
from .models import ModelsFromAutomapBase


class DatabaseHandler:
    def __init__(
        self,
        sqlalchemy_database_uri: PostgresDsn,
        schemas: List[str] = ["public", "sourcing", "user"],
    ):
        self.base = automap_base()
        self.engine = create_engine(sqlalchemy_database_uri, pool_pre_ping=True)
        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.models = ModelsFromAutomapBase(self.base)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for schema in schemas:
                self.base.prepare(self.engine, reflect=True, schema=schema)

        self.crud = CRUDInterface(self.models)

    def close(self):
        self.engine.dispose()
