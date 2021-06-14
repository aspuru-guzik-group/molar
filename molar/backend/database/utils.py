# std
from typing import Any, Container, Dict, Optional, Type
from uuid import UUID

# external
import sqlalchemy
from sqlalchemy import orm, sql
from sqlalchemy.dialects import postgresql
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

# Derived from from https://github.com/tiangolo/pydantic-sqlalchemy/blob/master/pydantic_sqlalchemy/main.py
# by Tiangolo. Distributed under MIT license.


def extract_fields(
    mapper,
    result,
    add_table_name: bool = False,
    exclude: Container[str] = [],
    table_name: Optional[str] = None,
):
    fields = {}
    if table_name is None:
        table_name = mapper.tables[0].name
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                value = getattr(result, name, None)
                if value is None:
                    continue
                column = attr.columns[0]
                if isinstance(column.type, postgresql.base.UUID):
                    value = UUID(value)
                if add_table_name:
                    name = f"{table_name}.{name}"
            fields[name] = value
    return fields


def sqlalchemy_to_dict(
    model: Type,
    result,
    type_,
    *,
    add_table_name: bool = False,
    exclude: Container[str] = [],
) -> Dict[str, Any]:
    if isinstance(model, orm.util.AliasedClass):
        alias_name = model._aliased_insp.name
        mapper = inspect(model).mapper
        return extract_fields(mapper, result, add_table_name, exclude, alias_name)

    elif isinstance(model, orm.decl_api.DeclarativeMeta):
        mapper = inspect(model)
        return extract_fields(mapper, result, add_table_name, exclude)

    elif isinstance(model, orm.attributes.InstrumentedAttribute):
        name = model.key
        value = result
        table_name = (
            model.parent.name
            if model.parent.is_aliased_class
            else model.parent.tables[0].name
        )
        if isinstance(model.type, postgresql.base.UUID):
            value = UUID(value)
        if add_table_name:
            name = f"{table_name}.{name}"
        return {name: value}

    elif isinstance(model, sql.elements.BinaryExpression):
        name = (
            type_
            if not add_table_name
            else f"{str(model.compile()).split('.')[1]}.{type_}"
        )
        value = result[0] if isinstance(result, sqlalchemy.engine.row.Row) else result
        return {name: value}

    raise ValueError(f"Could not handle model type {type(model)}")
