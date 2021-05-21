from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .... import database, models, schemas
from ....core import security
from ....core.config import settings
from ....core.security import get_password_hash
from ....crud import CRUDInterface
from ....utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)
from ... import deps

router = APIRouter()


@router.get("/get-users", response_model=schemas.User)
def get_users(
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve DB users
    :returns: List of tuples (user_id, user_email) 
    """

    
    if crud.user.is_superuser(current_user):
        users = crud.user.get_multi(
            db,
        )
    else:
        users = crud.user.get_multi_by_owner(db=db, owner=current_user.id)
    #TODO return something else here
    print([(user.user_id,user.email) for user in users])
    return [(user.user_id,user.email) for user in users]


@router.post("/add-user", response_model=schemas.Token)
def add_user(
    user_in: schemas.UserCreate,
    current_user=Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),

):
    
    #import ipdb
    #ipdb.set_trace()
    if crud.user.is_superuser(current_user):
        resp = crud.user.create(db, obj_in = user_in)
    #TODO check current_user's organization and if he is allowed to add this user?
    #also other checks here
    return resp
    
@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    crud: CRUDInterface = Depends(deps.get_crud),
) -> Any:
    """
    Get a specific user by id.
    """
    import ipdb
    ipdb.set_trace() 
    user = crud.user.get(db, user_id=user_id)

    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have sufficient privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user = Depends(deps.get_current_active_superuser),
    crud: CRUDInterface = Depends(deps.get_crud),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
