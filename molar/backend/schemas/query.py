# std
from enum import Enum
from typing import Any, List, Optional, Union

# external
from pydantic import BaseModel


class JoinType(str, Enum):
    inner = "inner"
    outer = "outer"
    full = "full"


class RelationshipOperators(str, Enum):
    eq = "=="
    ne = "!="
    gt = ">"
    lt = "<"
    ge = ">="
    le = "<="
    in_ = "in"
    not_in = "not_in"
    like = "like"
    ilike = "ilike"
    notlike = "notlike"
    notilike = "notilike"


class LogicalOperators(str, Enum):
    and_ = "and"
    or_ = "or"


class OrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class QueryAlias(BaseModel):
    type: str
    alias: str


class QueryJoinOnClause(BaseModel):
    column1: str
    column2: str


class QueryJoin(BaseModel):
    type: str
    join_type: JoinType = JoinType.inner
    on: Optional[QueryJoinOnClause] = None


class QueryFilter(BaseModel):
    type: str
    op: RelationshipOperators = RelationshipOperators.eq
    value: Union[Any]


class QueryFilterList(BaseModel):
    op: LogicalOperators = LogicalOperators.and_
    filters: List[Union[QueryFilter, "QueryFilterList"]]


class QueryOrderBy(BaseModel):
    type: str
    order: OrderEnum = "asc"


QueryFilterList.update_forward_refs()

QueryTypes = Union[str, List[str]]
QueryAliases = Union[QueryAlias, List[QueryAlias]]
QueryJoins = Union[List[QueryJoin], QueryJoin]
QueryFilters = Union[QueryFilter, QueryFilterList]
QueryOrderBys = Union[QueryOrderBy, List[QueryOrderBy]]
