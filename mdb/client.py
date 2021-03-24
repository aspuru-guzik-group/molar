import json
import logging
from typing import Optional

import numpy as np
import pandas as pd
import sqlalchemy
from rich.logging import RichHandler
from sqlalchemy import and_, text
from tqdm import tqdm

from . import database as db
from .config import ClientConfig
from .registry import REGISTRIES

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

        self.dao = DataAccessObject(self.session, self.models)

        capabilities = db.fetch_database_capabilities(self.session)

        for mapper in REGISTRIES["mappers"]:
            setattr(
                self,
                mapper["name"],
                self.mapper_decorator(mapper["func"], mapper["table"]),
            )

        for query in REGISTRIES["queries"]:
            setattr(
                self, query["name"], self.query_decorator(query["func"], query["table"])
            )

        for sql_query in REGISTRIES["sql"]:
            setattr(
                self,
                sql_query["name"],
                self.sql_query_decorator(sql_query["func"]),
            )

    def __delete__(self):
        self.session.close()

    def mapper_decorator(self, func, table):
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

    def query_decorator(self, func, table):
        def inner(*args, **kwargs):
            query = func(*args, **kwargs)
            data = self.dao.get(table, **query)
            if self.cfg.return_pandas_dataframe:
                records = [d.__dict__ for d in data]
                df = pd.DataFrame.from_records(records)
                return df.replace({np.nan: None})
            return data

        return inner

    def sql_query_decorator(self, func):
        def inner(*args, **kwargs):
            sql = text(func(*args, **kwargs))
            data = self.session.execute(sql).fetchall()
            # TODO what if we want a dataframe here?
            return data

        return inner


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
