# std
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

# external
from pydantic import BaseModel


class EventTypes(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"
    rollback = "rollback"
    rollback_begin = "rollback-begin"
    rollback_end = "rollback-end"


class EventStoreBase(BaseModel):
    type: Optional[str]


class EventStore(EventStoreBase):
    id: Optional[int]
    uuid: Optional[UUID]
    event: EventTypes
    data: Dict[str, Any]
    timestamp: Optional[datetime]
    alembic_version: Optional[List[str]]
    user_id: Optional[int]


class EventStoreCreate(EventStoreBase):
    data: Dict[str, Any]


class EventStoreDelete(EventStoreBase):
    uuid: UUID


class EventStoreUpdate(EventStoreBase):
    uuid: UUID
    data: Dict[str, Any]
