# std
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

# external
from pydantic import BaseModel


class EventTypes(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"
    rollback = "rollback"


class EventStoreBase(BaseModel):
    type: str


class EventStore(EventStoreBase):
    uuid: Optional[UUID]
    event: EventTypes
    data: Dict[str, Any]
    timestamp: Optional[datetime]


class EventStoreCreate(EventStoreBase):
    data: Dict[str, Any]


class EventStoreDelete(EventStoreBase):
    uuid: UUID


class EventStoreUpdate(EventStoreBase):
    uuid: UUID
    data: Dict[str, Any]
