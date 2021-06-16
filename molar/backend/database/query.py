# std
from typing import Any, Dict, List, Optional, Union

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


def resolve_type(type: str, models, alias_registry=None):
    if alias_registry is None:
        alias_registry = {}

    types = type.split(".")

    if len(types) == 1:
        if isinstance(models, sqlalchemy.orm.attributes.InstrumentedAttribute):
            return models[types[0]].astext

        type_ = getattr(models, types[0], None)
        if type_ is not None:
            return type_

        if types[0] in alias_registry.keys():
            return alias_registry[types[0]]

        raise ValueError(f"Type {type} not found in database!")

    submodel = getattr(models, types[0], None)

    if submodel is None and types[0] in alias_registry.keys():
        submodel = alias_registry[types[0]]

    if submodel is not None:
        return resolve_type(".".join(types[1:]), submodel, alias_registry)
    raise ValueError(f"Type {type} not found in database!")


def query_builder(
    db: Session,
    models,
    types: schemas.QueryTypes,
    limit: int,
    offset: int,
    joins: Optional[schemas.QueryJoins] = None,
    filters: Optional[schemas.QueryFilters] = None,
    order_by: Optional[schemas.QueryOrderBys] = None,
    aliases: Optional[schemas.QueryAliases] = None,
):
    alias_registry: Dict[str, Any] = {}

    # Resolving aliases
    if aliases is not None:
        if not isinstance(aliases, list):
            aliases = [aliases]

        for alias in aliases:
            alias_registry[alias.alias] = aliased(
                resolve_type(alias.type, models), name=alias.alias
            )

    # Resolving main types
    if not isinstance(types, list):
        types = [types]

    db_objs = []
    for type_ in types:
        db_obj = resolve_type(type_, models, alias_registry)
        db_objs.append(db_obj)

    query = db.query(*db_objs)

    if joins is not None:
        if not isinstance(joins, list):
            joins = [joins]
        for join in joins:
            joined_table = resolve_type(
                join.type,
                models,
                alias_registry,
            )
            onclause = None
            if join.on is not None:
                onclause = resolve_type(
                    join.on.column1, models, alias_registry
                ) == resolve_type(join.on.column2, models, alias_registry)

            query = query.join(
                joined_table,
                onclause,
                isouter=True if join.join_type == "outer" else False,
                full=True if join.join_type == "full" else False,
            )

    if filters is not None:
        filters = expand_filters(filters, models, alias_registry)
        query = query.filter(filters)

    if order_by is not None:
        if not isinstance(order_by, list):
            order_by = [order_by]
        order_bys = []
        for ob in order_by:
            t = resolve_type(ob.type, models, alias_registry)
            if ob.order == "asc":
                order_bys.append(t.asc())
            else:
                order_bys.append(t.desc())
        query = query.order_by(*order_bys)

    query = query.offset(offset).limit(limit)
    return query, db_objs, types


def process_query_output(db_objs, query_results, types):
    if len(db_objs) == 1:
        return [sqlalchemy_to_dict(db_objs[0], r, types[0]) for r in query_results]

    results = []
    for result in query_results:
        result_dict = {}
        for res, db_obj, t in zip(result, db_objs, types):
            result_dict.update(sqlalchemy_to_dict(db_obj, res, t, add_table_name=True))
        results.append(result_dict)
    return results


def expand_filters(filters, models, alias_registry):
    if isinstance(filters, schemas.QueryFilterList):
        filters = [expand_filters(f) for f in filters.filters]
        if filters.op == "and":
            return sqlalchemy.and_(*filters)
        elif filters.op == "or":
            return sqlalchemy.or_(*filters)
        else:
            raise ValueError(f"Filter operator not supported: {filters.op}")

    elif isinstance(filters, schemas.QueryFilter):
        type = resolve_type(filters.type, models, alias_registry)
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
                value_type = resolve_type(value, models, alias_registry)
            except ValueError:
                pass
            else:
                value = value_type

        return getattr(type, operator)(value)
