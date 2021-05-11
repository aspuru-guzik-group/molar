from molar.backend.schemas.eventstore import (
    EventStoreCreate,
    EventStoreDelete,
    EventStoreUpdate,
)
from sqlalchemy.orm import Session

from .base import CRUDBase, ModelType


class CRUDEventStore(CRUDBase[ModelType, EventStoreCreate, EventStoreUpdate]):
    def create(self, db: Session, obj_in: EventStoreCreate):
        super().create(db, obj_in=obj_in)

    def update(self, db: Session, obj_in: EventStoreUpdate):
        super().create(db, obj_in=obj_in)

    def delete(self, db: Session, obj_in: EventStoreUpdate):
        super().create(db, obj_in=obj_in)

    def rollback(self, db: Session):
        pass
