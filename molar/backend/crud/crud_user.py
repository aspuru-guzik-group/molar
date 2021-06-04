# std
from datetime import datetime
from typing import Any, Dict, Optional, Union

# external
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from ..core.security import get_password_hash, verify_password
from ..schemas.user import UserCreate, UserUpdate
from .base import CRUDBase, ModelType


class CRUDUser(CRUDBase[ModelType, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> ModelType:
        db_obj = self.model(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
            created_on=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data.keys():
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove_by_email(self, db, *, email: str):
        db_obj = self.get_by_email(db, email=email)
        db.delete(db_obj)
        db.commit()
        return db_obj

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[ModelType]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: ModelType) -> bool:
        return user.is_active

    def activate(self, db: Session, *, db_obj) -> ModelType:

        setattr(db_obj, "is_active", True)
        # if not getattr(db_obj, "is_active"):
        #     raise InvalidRequestError()
        # return db_obj
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def deactivate(self, db: Session, *, db_obj) -> ModelType:
        setattr(db_obj, "is_active", False)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def is_superuser(self, user: ModelType) -> bool:
        return user.is_superuser
