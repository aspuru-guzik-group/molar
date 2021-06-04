# std
from typing import Any, List

# external
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
import sqlalchemy
from sqlalchemy.orm import Session

# molar
from molar.backend import schemas
from molar.backend.core.config import settings
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
        "is_active": db_obj.is_active,
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
        db_obj = crud.user.create(db, obj_in=obj_in)
        # crud.user.deactivate(db, db_obj=db_obj)
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
    resp = crud.user.activate(db, db_obj=db_obj)
    # if resp.is_active:
    #     raise HTTPException(status_code=404, detail="is_active is True")
    # return {
    #     "email": resp.email,
    #     "full_name": resp.full_name,
    #     "created_on": resp.created_on,
    #     "is_active": resp.is_active,
    #     "is_superuser": resp.is_superuser,
    # }
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
    updated = crud.user.deactivate(db, db_obj=db_obj)
    # return {
    #     "email": updated.email,
    #     "full_name": updated.full_name,
    #     "created_on": updated.created_on,
    #     "is_activate": updated.is_active,
    #     "is_superuser": updated.is_superuser,
    # }
    return {"msg": f"User {email} is now deactivated!"}


@router.patch("/", response_model=schemas.Msg)
def update_user(
    email: EmailStr,
    password: str = Body(None),
    full_name: str = Body(None),
    is_superuser: bool = Body(None),
    is_active: bool = Body(None),
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
    crud: CRUDInterface = Depends(deps.get_crud),
) -> Any:
    current_user_data = jsonable_encoder(crud.user.get_by_email(db, email=email))
    user_in = schemas.UserUpdate(**current_user_data)
    if email != current_user.email and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="You don't have sufficient permission."
        )

    if (
        is_superuser is not None or is_active is not None
    ) and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Nice try!")
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    if is_active is not None:
        user_in.is_active = is_active
    if is_superuser is not None:
        user_in.is_superuser = is_superuser
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return {"msg": f"User {user.email} has been updated!"}


# @router.patch("/superuser", response_model=schemas.Msg)
# def grant_superuser_rights(
#     email: EmailStr,
#     new_is_superuser: bool,
#     db: Session = Depends(deps.get_db),
#     current_user = Depends(deps.get_current_active_user),
#     crud: CRUDInterface = Depends(deps.get_crud),
# ):
#     if current_user.email != email and not crud.user.is_superuser(current_user):
#         raise HTTPException(
#             status_code=401, detail="You don't have sufficient permission"
#         )

#     user = crud.user.get_by_email(db, email=email)

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user.is_superuser:
#         return {"msg": f"User {email} is already a superuser"}

#     if not crud.user.is_superuser(current_user):
#         raise HTTPException(status_code=401, detail="Nice try!")

#     user_update_model = {
#         "email": email,
#         "password": user.password,
#         "organization": user.organization,
#         "is_active": user.is_active,
#         "is_superuser": new_is_superuser,
#         "full_name": user.full_name,
#     }
#     user = crud.user.update(db, db_obj=user, obj_in=user_update_model)

#     return {"msg": f"User {email} now has superuser rights"}

# @router.patch("/password", response_model=schemas.Msg)
# def update_password(
#     email: EmailStr,
#     old_password: bool,
#     new_password: bool,
#     db: Session = Depends(deps.get_db),
#     current_user = Depends(deps.get_current_active_user),
#     crud: CRUDInterface = Depends(deps.get_crud),
# ):
#     if current_user.email != email and not crud.user.is_superuser(current_user):
#         raise HTTPException(
#             status_code=401, detail="You don't have sufficient permission"
#         )

#     user = crud.user.get_by_email(db, email=email)

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if not crud.user.is_superuser(current_user):
#         raise HTTPException(status_code=401, detail="Only superusers can change passwords")

#     if not verify_password(old_password, user.password):
#         raise HTTPException(status_code=401, detail="Passwords do not match")

#     user_update_model = {
#         "email": email,
#         "password": new_password,
#         "organization": user.organization,
#         "is_active": user.is_active,
#         "is_superuser": user.is_supervisor,
#         "full_name": user.full_name,
#     }
#     user = crud.user.update(db, db_obj=user, obj_in=user_update_model)

#     return {"msg": f"User {email} now has superuser rights"}


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
