# std
from typing import List, Optional, Union

# external
import pkg_resources
import sqlalchemy
from sqlalchemy.orm import aliased, Session

# molar
from molar.backend import schemas
from molar.backend.database.utils import sqlalchemy_to_dict

INFORMATION_QUERY = open(
    pkg_resources.resource_filename("molar", "sql/information_query.sql"), "r"
).read()


def resolve_type(type: str, models):
    type = type.split(".")
    if len(type) == 1:
        # if json
        if isinstance(models, sqlalchemy.orm.attributes.InstrumentedAttribute):
            return models[type[0]].astext
        type_ = getattr(models, type[0], None)
        if type_ is None:
            raise ValueError(f"Type {type} not found in database!")
        return type_
    models = getattr(models, type[0], None)
    return resolve_type(".".join(type[1:]), models)


def query_builder(
    db: Session,
    models,
    types: Union[str, List[str]],
    limit: int,
    offset: int,
    joins: Optional[Union[List[schemas.QueryJoin], schemas.QueryJoin]] = None,
    filters: Optional[Union[schemas.QueryFilter, schemas.QueryFilterList]] = None,
    order_by: Optional[Union[str, List[str]]] = None,
):
    if not isinstance(types, list):
        types = [types]

    db_objs = []
    for type_ in types:
        db_obj = resolve_type(type_, models)
        db_objs.append(db_obj)

    query = db.query(*db_objs)

    if joins is not None:
        if not isinstance(joins, list):
            joins = [joins]
        for join in joins:
            joined_table = resolve_type(join.type, models)
            if join.alias is not None:
                joined_table = aliased(joined_table, name=join.alias)
            onclause = None
            if join.on is not None:
                onclause = resolve_type(join.on.column1, models) == resolve_type(
                    join.on.column2, models
                )

            query = query.join(
                joined_table,
                onclause,
                isouter=True if join.join_type == "outer" else False,
                full=True if join.join_type == "full" else False,
            )

    if filters is not None:
        filters = expand_filters(filters, models)
        query = query.filter(filters)

    if order_by is not None:
        if not isinstance(order_by, list):
            order_by = [order_by]
        query.order_by([resolve_type(t) for t in order_by])

    query_results = query.offset(offset).limit(limit).all()

    if len(db_objs) == 1:
        return [sqlalchemy_to_dict(db_objs[0], r, types[0]) for r in query_results]

    results = []
    for result in query_results:
        result_dict = {}
        for res, db_obj, t in zip(result, db_objs, types):
            result_dict.update(sqlalchemy_to_dict(db_obj, res, t, add_table_name=True))
        results.append(result_dict)
    return results


def expand_filters(filters, models):
    if isinstance(filters, schemas.QueryFilterList):
        filters = [expand_filters(f) for f in filters.filters]
        if filters.op == "and":
            return sqlalchemy.and_(*filters)
        elif filters.op == "or":
            return sqlalchemy.or_(*filters)
        else:
            raise ValueError(f"Filter operator not supported: {filters.op}")

    elif isinstance(filters, schemas.QueryFilter):
        type = resolve_type(filters.type, models)
        operator = filters.op
        if filters.op == "==":
            operator = "__eq__"
        elif filters.op == "!=":
            operator = "__ne__"
        elif filters.op == ">":
            operator = "__gt__"
        elif filters.op == "<":
            operator = "__lt__"
        elif filters.op == ">=":
            operator = "__ge__"
        elif filters.op == "<=":
            operator = "__le__"

        # If value is another column
        value = filters.value
        if isinstance(value, str):
            try:
                value_type = resolve_type(value, models)
            except ValueError:
                pass
            else:
                value = value_type

        return getattr(type, operator)(value)
