from enum import Enum
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel


class EventTypes(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"
    rollback = "rollback"


class EventStoreBase(BaseModel):
    event: EventTypes
    type: str
    data: Dict[str, Any]


class EventStoreCreate(EventStoreBase):
    pass

class EventStoreDelete(EventStoreBase):
    pass
class EventStoreUpdate(EventStoreCreate):
    uuid: UUID
