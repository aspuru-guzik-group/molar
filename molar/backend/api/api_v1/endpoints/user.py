# std
from datetime import timedelta
from typing import Any, List

# external
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
import sqlalchemy
from sqlalchemy.orm import Session

# molar
from molar.backend import database, models, schemas
from molar.backend.core import security
from molar.backend.core.config import settings
from molar.backend.core.security import get_password_hash
from molar.backend.crud import CRUDInterface
from molar.backend.utils import send_new_account_email
from ... import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.UserBase])
def get_users(
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_user),
):
    if crud.user.is_superuser(current_user):
        users = crud.user.get_multi(
            db,
        )
    else:
        users = crud.user.get_multi_by_owner(db=db, owner=current_user.id)
    return [
        {
            "email": u.email,
            "full_name": u.full_name,
            "created_on": u.created_on,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
        }
        for u in users
    ]


@router.get("/{email}", response_model=schemas.UserBase)
def get_user_by_email(
    email: EmailStr,
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_user),
):
    db_obj = crud.user.get_by_email(db, email=email)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "email": db_obj.email,
        "full_name": db_obj.full_name,
        "created_on": db_obj.created_on,
        "is_activate": db_obj.is_active,
        "is_superuser": db_obj.is_superuser,
    }


@router.post("/add", response_model=schemas.Msg)
def add_a_user(
    user_in: schemas.UserCreate,
    database_name: str = "molar_main",
    current_user=Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
):

    try:
        crud.user.create(db, obj_in=user_in)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=401, detail="This username is already taken.")
    if settings.EMAILS_ENABLED:
        send_new_account_email(email_to=user_in.email, database=database_name)
    return {"msg": f"User {user_in.email} created"}


@router.post("/register", response_model=schemas.Msg)
def register_a_new_user(
    user_in: schemas.UserRegister,
    database_name: str = "molar_main",
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
):
    obj_in = schemas.UserCreate(
        full_name=user_in.full_name,
        email=user_in.email,
        password=user_in.password,
        is_active=False,
        is_superuser=False,
    )
    try:
        crud.user.create(db, obj_in=obj_in)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=401, detail="This username is already taken.")
    if settings.EMAILS_ENABLED:
        send_new_account_email(email_to=user_in.email, database=database_name)
    return {
        "msg": (
            f"User {user_in.email} has been register."
            " Ask your database admin to activate this account"
        )
    }


@router.patch("/activate", response_model=schemas.Msg)
def activate_user(
    email: EmailStr,
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_superuser),
):
    db_obj = crud.user.get_by_email(db, email=email)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    crud.user.activate(db, db_obj=db_obj)
    return {"msg": f"User {email} is now active!"}


@router.patch("/deactivate", response_model=schemas.Msg)
def deactivate_user(
    email: EmailStr,
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_superuser),
):

    db_obj = crud.user.get_by_email(db, email=email)
    if not db_obj:
        raise HTTPException(status_code=404, detail="User not found")
    crud.user.deactivate(db, db_obj=db_obj)
    return {"msg": f"User {email} is now deactivated!"}


@router.patch("/", response_model=schemas.Msg)
def update_user(
    user_in: schemas.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
    crud: CRUDInterface = Depends(deps.get_crud),
) -> Any:
    if current_user.email != user_in.email and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=401, detail="You don't have sufficient permission"
        )

    user = crud.user.get_by_email(db, email=user_in.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not crud.user.is_superuser(current_user) and user_in.is_superuser:
        raise HTTPException(status_code=401, detail="Nice try!")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return {"msg": f"User {user_in.email} has been updated!"}


@router.delete("/", response_model=schemas.Msg)
def delete_user(
    email: EmailStr,
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_superuser),
):
    if not crud.user.get_by_email(db, email=email):
        raise HTTPException(status_code=404, detail="User not found!")
    crud.user.remove_by_email(db, email=email)

    return {"msg": f"User {email} has been deleted!"}
