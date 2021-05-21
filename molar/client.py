import configparser
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd
import sqlalchemy
from rich.logging import RichHandler
from sqlalchemy import and_, text
from tqdm import tqdm

from . import database as db
from .config import ClientConfig
from .mappers import *
from .registry import REGISTRIES, compute_requirement_score

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


class Client:
    def __init__(
        self,
        cfg: ClientConfig,
        logger: Optional[logging.Logger] = None,
    ):

        self.cfg = cfg
        Session, engine, models = db.init_database(self.cfg.sql_url)
        self.session = Session()
        self.engine = engine
        self.models = models
        self.logger = logger or logging.getLogger("molar")

        if self.logger:
            self.logger.setLevel(cfg.log_level)

        # self.dao = DataAccessObject(self.session, self.models)

        self.database_specs = db.fetch_database_specs(self.session)

        self.registered_mappers = {}
        self.registered_queries = {}
        self.registered_sql = {}

        self.set_registry_functions(
            REGISTRIES["mappers"], self.mapper_decorator, self.registered_mappers
        )
        self.set_registry_functions(
            REGISTRIES["queries"], self.query_decorator, self.registered_queries
        )
        self.set_registry_functions(
            REGISTRIES["sql"], self.sql_query_decorator, self.registered_sql
        )

    def set_registry_functions(
        self, registry: List[Dict], decorator: Callable, internal_registry: Dict
    ) -> None:
        items_to_use = {}
        for item in registry:
            requirements_score = compute_requirement_score(
                self.database_specs, item["requirements"], item["requirements_bonus"]
            )
            item["score"] = requirements_score
            if item["name"] not in items_to_use.keys():
                items_to_use[item["name"]] = item
                continue

            if requirements_score > items_to_use[item["name"]]["score"]:
                items_to_use[item["name"]] = item

        for name, item in items_to_use.items():
            if getattr(self, name, None) is not None:
                raise ValueError(
                    f"{name} is already used! Please use another name for this function"
                )

            setattr(self, name, decorator(item["func"], item["table"]))
            internal_registry[name] = item["func"]

    @staticmethod
    def from_config_file(config_file: str, section_name: str = None) -> "Client":
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        if section_name is None:
            section_name = config_parser.sections()[0]

        assert (
            section_name in config_parser
        ), f"Section {section_name} could not be found in the config file {config_file}"
        config = ClientConfig.from_dict(config_parser[section_name])
        return Client(config)

    @staticmethod
    def login(hostname: str, database: str, username: str, password: str) -> "Client":
        if (not os.path.exists(ClientConfig.DEFAULT_DIRECTORY)):
            os.mkdir(ClientConfig.DEFAULT_DIRECTORY)
        
        filepath = os.path.join(ClientConfig.DEFAULT_DIRECTORY, "database.ini")
        config_parser = configparser.ConfigParser()
        
        if (not os.path.exists(filepath)):            
            config_parser[username] = {
                'hostname': hostname,
                'database': database,
                'username': username,
                'password': password
            }
            with open(filepath, 'w') as configfile:
                config_parser.write(configfile)
        else:
            config_parser.read(filepath)
            if (not config_parser.has_section(username)):
                config_parser[username] = {
                    'hostname': hostname,
                    'database': database,
                    'username': username,
                    'password': password
                }
            with open(filepath, 'a') as configfile:
                config_parser.write(configfile)
        return Client.from_config_file(config_file=filepath, section_name= username)
        
    def check_token():
        pass
        
    

    def __delete__(self):
        self.session.close()

    def mapper_decorator(self, func: Callable, table: str) -> Callable:
        def inner(*args, **kwargs):
            data = func(*args, **kwargs)
            event = self.dao.add(table, data)
            issue = self.dao.commit_or_fetch_event(table, data)
            if issue:
                self.logger.warn(
                    (
                        f"Could not add new row to table {table} "
                        f"with data {data} because it already exists!"
                    )
                )
                return issue
            self.logger.debug(f"Adding item to table {table} with data {data}")
            return event

        return inner

    def query_decorator(
        self, func: Callable, table: str, return_pandas_dataframe=None
    ) -> Callable:
        def inner(*args, **kwargs):
            if return_pandas_dataframe is None:
                return_pandas_dataframe = self.cfg.return_pandas_dataframe
            query = func(self.models, *args, **kwargs)
            data = self.dao.get(table, **query)
            if return_pandas_dataframe:
                records = [d.__dict__ for d in data]
                df = pd.DataFrame.from_records(records)
                return df.replace({np.nan: None})
            return data

        return inner

    def sql_query_decorator(self, func: Callable, table: str) -> Callable:
        def inner(*args, **kwargs):
            sql = text(func(*args, **kwargs))
            data = self.session.execute(sql).fetchall()
            # TODO what if we want a dataframe here?
            return data

        return inner

    def get(
        self,
        table: str,
        filters: Optional[List] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Any] = None,
    ):
        if table not in self.database_specs["table"]:
            raise ValueError(
                f"Table {table} does not exisits in the database {self.cfg.database}!"
            )
        return self.dao.get(table, filters, limit, offset, order_by)


class DataAccessObject:
    """Defines the low level interactions between MDBClient and the database.
    It is not meant to be used on its own.

    :session: (sqlalchemy.orm.session.Session)
    :models: (sqlalchemy.orm.mapper)
    """

    def __init__(self, session, models):
        self.session = session
        self.models = models

    def get(self, table_name, filters=None, limit=None, offset=None, order_by=None):
        """Reads data from a table.

        :param table_name (str):
        :param filters (list):
        :param limit (int or None):
        :param offset (int or None):
        :param order_by (asc or desc clause):
        """

        if not isinstance(table_name, list):
            table_name = [table_name]

        t = table_name.pop(0)
        model = getattr(self.models, t, None)
        assert model is not None, f"{t} does not correspond to any table!"

        order_by_col = getattr(model, "updated_on", None)
        if order_by_col is None:
            order_by_col = getattr(model, "timestamp", None)

        if order_by is None:
            order_by = order_by_col.desc()
        query = self.session.query(model)

        for t in table_name:
            model = getattr(self.models, t, None)
            assert model is not None, f"{t} does not correspond to any table!"
            query = query.join(model)

        if filters is not None:
            filter = True
            for f in filters:
                filter = and_(filter, f)
            query = query.filter(filter)
        query = query.order_by(order_by)

        if limit is None:
            return query.all()

        if offset is not None:
            query = query.offset(offset)
        query = query.limit(limit)

        return query

    def add(self, table_name, data):
        """Adds data to the database. This corresponds to a 'create' event on
        the eventstore with a 'type' of table_name.

        :param table_name:
        :param data:
        """
        params = {"event": "create", "type": table_name, "data": data}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def delete(self, table_name, id):
        """Deletes data from the databse. This corresponds to a 'delete' event
        on the eventstore with a 'type' of table_name.

        :param table_name:
        :param id:
        """
        params = {"event": "delete", "type": table_name, "uuid": id}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def update(self, table_name, data, id):
        """Updates data from the database. This corresponds to an 'update'
        event on the eventstore with a 'type' of table_name.

        :param table_name:
        :param data:
        :param id:
        """
        params = {"event": "update", "type": table_name, "data": data, "uuid": id}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def rollback(self, before):
        """Rollback the database. This corresponds to a 'rollback' event on the
        eventstore. For now, until rollback to a specific date is available.

        :param before: (datetime.dateime)
        """

        params = {"event": "rollback", "data": {"before": before.isoformat()}}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def commit_or_fetch_event(self, table_name, data):
        """Tries to commit the current transation and if it fails, fetches the
        corresponding event in the eventstore table."""
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as ex:
            if "UniqueViolation" in ex._message():
                self.session.rollback()
                filters = ""
                for k, v in data.items():
                    if isinstance(v, dict):
                        filters += f"data->'{k}' = '{json.dumps(v)}'::jsonb and "
                        continue
                    filters += f"data->>'{k}' = '{v}' and "

                # Single query to retrieve the event
                sql = text(
                    f"""
                    select uuid,
                           type,
                           jsonb_agg(data)->>-1 as data,
                           string_agg("event", ',') as event,
                           max(timestamp) as timestamp
                      from sourcing.eventstore
                      join {table_name}
                        on eventstore.uuid = {table_name}_id
                     where {filters[:-4]}
                  group by uuid, type
                    having not right(string_agg("event", ','), 6) = 'delete'
                  order by min(eventstore.id) asc;
                """
                )
                out = self.session.execute(sql).fetchall()
                # It's a UniqueViolation... there should be only one
                if len(out) != 1:
                    raise ex

                # Returning uuid as str
                out[0]._processors[0] = lambda x: str(x)
                return out[0]
            else:
                self.session.rollback()
                raise ex
