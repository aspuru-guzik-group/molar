from typing import Generator, Optional

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


# TODO add type annotation for return type
def get_current_user(
    db: Session = Depends(get_db),
    crud: CRUDInterface = Depends(get_crud),
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
    user = crud.user.get(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
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
