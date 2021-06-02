# std
from typing import Generator, Optional

# external
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..core import security
from ..core.config import settings
from ..crud import CRUDInterface

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_main_db() -> Generator:
    try:
        session = database.main.session_local()
        yield session
    finally:
        session.close()


def get_main_crud():
    return database.main.crud


def get_main_current_user(
    db: Session = Depends(get_main_db),
    crud: CRUDInterface = Depends(get_main_crud),
    token: str = Depends(reusable_oauth2),
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if token_data.db != "main":
        raise HTTPException(status_code=403, detail="Not allowed on this database")
    user = crud.user.get(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_main_current_active_user(
    crud: CRUDInterface = Depends(get_main_crud),
    current_main_user=Depends(get_main_current_user),
):
    if not crud.user.is_active(current_main_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_main_user


def get_main_current_active_superuser(
    crud: CRUDInterface = Depends(get_main_crud),
    current_user=Depends(get_main_current_active_user),
):
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user does not have enough privileges"
        )
    return current_user


def get_db(database_name: Optional[str] = "main") -> Generator:
    try:
        base = getattr(database, database_name)
        if base is None:
            yield None
        else:
            session = base.session_local()
            yield session
    finally:
        if base is not None:
            session.close()


def get_crud(database_name: Optional[str] = "main"):
    base = getattr(database, database_name)
    if base is None:
        return None
    return base.crud


def get_models(database_name: Optional[str] = "main"):
    base = getattr(database, database_name)
    if base is None:
        return None
    return base.models


def get_current_user(
    database_name: str = "main",
    db: Session = Depends(get_db),
    crud: CRUDInterface = Depends(get_crud),
    token: str = Depends(reusable_oauth2),
):
    if db is None:
        raise HTTPException(status_code=404, detail="Database not found")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    if token_data.db != database_name:
        raise HTTPException(status_code=403, detail="Not allowed on this database")

    if crud is None or not hasattr(crud, "user"):
        raise HTTPException(status_code=404, detail="User table not found")

    user = crud.user.get(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    crud: CRUDInterface = Depends(get_crud),
    current_user=Depends(get_current_user),
):
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    crud: CRUDInterface = Depends(get_crud),
    current_user=Depends(get_current_user),
):
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
