from enum import Enum
from typing import Any, List, Union

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


class QueryJoin(BaseModel):
    type: str
    join_type: JoinType = JoinType.inner


class QueryFilter(BaseModel):
    type: str
    op: RelationshipOperators = RelationshipOperators.eq
    value: Union[Any]


class QueryFilterList(BaseModel):
    op: LogicalOperators = LogicalOperators.and_
    filters: List[Union[QueryFilter, "QueryFilterList"]]


QueryFilterList.update_forward_refs()
