# std
from typing import List

# external
from fastapi import APIRouter, Depends, HTTPException
import sqlalchemy
from sqlalchemy.orm import Session

# molar
from molar.backend import schemas
from molar.backend.api import deps

router = APIRouter()


@router.get("/{database_name}", response_model=List[schemas.EventStore])
def view_eventstore(
    database_name: str,
    db: Session = Depends(deps.get_db),
    crud=Depends(deps.get_crud),
    current_user=Depends(deps.get_current_active_user),
):
    if crud.eventstore is None:
        raise HTTPException(status_code=404, detail="Eventstore not found")
    db_obj = crud.eventstore.get_all(db)
    return [
        schemas.EventStore(
            uuid=obj.uuid,
            event=obj.event,
            type=obj.type,
            timestamp=obj.timestamp,
            data=obj.data,
        )
        for obj in db_obj
    ]


@router.post("/{database_name}", response_model=schemas.EventStore)
def create(
    database_name: str,
    event: schemas.EventStoreCreate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
    crud=Depends(deps.get_crud),
):
    if crud.eventstore is None:
        raise HTTPException(status_code=404, detail="Eventstore not found")
    obj_out = crud.eventstore.create(db, obj_in=event, user_id=current_user.user_id)
    return schemas.EventStore(
        uuid=obj_out.uuid,
        event=obj_out.event,
        type=obj_out.type,
        timestamp=obj_out.timestamp,
        data=obj_out.data,
    )


@router.patch("/{database_name}", response_model=schemas.EventStore)
def update(
    database_name: str,
    event: schemas.EventStoreUpdate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
    crud=Depends(deps.get_crud),
):
    if crud.eventstore is None:
        raise HTTPException(status_code=404, detail="Eventstore not found")
    try:
        obj_out = crud.eventstore.update(db, obj_in=event, user_id=current_user.user_id)
    except sqlalchemy.exc.InternalError as e:
        raise HTTPException(
            status_code=404, detail="Event with uuid {event.uuid} not found!"
        )
    return schemas.EventStore(
        uuid=obj_out.uuid,
        event=obj_out.event,
        type=obj_out.type,
        timestamp=obj_out.timestamp,
        data=obj_out.data,
    )


@router.delete("/{database_name}", response_model=schemas.EventStore)
def delete(
    database_name: str,
    event: schemas.EventStoreDelete,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
    crud=Depends(deps.get_crud),
):
    if crud.eventstore is None:
        raise HTTPException(status_code=404, detail="Eventstore not found")
    obj_out = crud.eventstore.delete(db, obj_in=event, user_id=current_user.user_id)
    return schemas.EventStore(
        uuid=obj_out.uuid,
        event=obj_out.event,
        type=obj_out.type,
        timestamp=obj_out.timestamp,
        data=obj_out.data,
    )
