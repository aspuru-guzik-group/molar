# external
from sqlalchemy.orm import Session

from ..core.security import get_password_hash
from ..schemas.database import DatabaseCreate, DatabaseUpdate
from .base import CRUDBase, ModelType


class CRUDMolarDatabase(CRUDBase[ModelType, DatabaseCreate, DatabaseUpdate]):
    def get_by_database_name(self, db: Session, *, database_name: str):
        return (
            db.query(self.model)
            .filter(self.model.database_name == database_name)
            .first()
        )

    def create(self, db: Session, obj_in: DatabaseCreate):
        db_obj = self.model(
            database_name=obj_in.database_name,
            superuser_fullname=obj_in.superuser_fullname,
            superuser_email=obj_in.superuser_email,
            superuser_password=get_password_hash(obj_in.superuser_password),
            is_approved=False,
            alembic_revisions=obj_in.alembic_revisions,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def approve(self, db: Session, *, db_obj) -> ModelType:
        setattr(db_obj, "is_approved", True)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_by_database_name(self, db: Session, *, database_name: str):
        db_obj = self.get_by_database_name(db, database_name=database_name)
        db.delete(db_obj)
        db.commit()
        return db_obj
