# std
from datetime import datetime

# external
from sqlalchemy.orm import Session

# molar
from molar.backend.schemas.eventstore import (
    EventStore,
    EventStoreCreate,
    EventStoreDelete,
    EventStoreUpdate,
    EventTypes,
)

from .base import CRUDBase, ModelType


class CRUDEventStore(CRUDBase[ModelType, EventStoreCreate, EventStoreUpdate]):
    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create(self, db: Session, *, obj_in: EventStoreCreate, user_id: int):
        db_obj = self.model(
            event="create", type=obj_in.type, data=obj_in.data, user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, obj_in: EventStoreUpdate, user_id: int):
        db_obj = self.model(
            event="update",
            uuid=str(obj_in.uuid),
            type=obj_in.type,
            data=obj_in.data,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, obj_in: EventStoreDelete, user_id: int):
        db_obj = self.model(
            event="delete", type=obj_in.type, uuid=str(obj_in.uuid), user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def rollback(self, db: Session, *, before: datetime, user_id: int):
        db_obj = self.model(
            event="rollback", data={"before": str(before)}, user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
