from typing import Optional,Union
from pydantic import BaseModel,Json
from uuid import UUID
from datetime import datetime

class EventStoreBase(BaseModel):
    id: int
    timestamp: datetime = datetime.utcnow()
    uuid:Union[int, UUID]
    data: Json
    event:
    type:

