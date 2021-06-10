# std
from typing import List

# external
import alembic
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
import sqlalchemy
from sqlalchemy.orm import Session

# molar
from molar import install
from molar.backend import alembic_utils, database, schemas
from molar.backend.api import deps
from molar.backend.core.config import settings
from molar.backend.crud import CRUDInterface
from molar.backend.database.query import INFORMATION_QUERY
from molar.backend.utils import send_database_created_email

router = APIRouter()


@router.post("/request", response_model=schemas.Msg)
def database_creation_request(
    database_in: schemas.DatabaseCreate,
    db: Session = Depends(deps.get_main_db),
    crud: CRUDInterface = Depends(deps.get_main_crud),
):
    if database_in.database_name in ["molar_main", "main"]:
        raise HTTPException(
            status_code=401, detail="This database name is already taken"
        )

    try:
        crud.molar_database.create(db, obj_in=database_in)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=401, detail="This database name is already taken"
        )

    return {"msg": "Database request created"}


@router.get("/requests")
def get_database_requests(
    db: Session = Depends(deps.get_main_db),
    current_user=Depends(deps.get_main_current_active_superuser),
):
    out = db.query(database.main.models.molar_database).all()
    return out


@router.get("/information", response_model=List[schemas.DatabaseInformation])
def get_database_information(
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
):
    results = db.execute(INFORMATION_QUERY).all()
    column_names = [
        "table_name",
        "column_name",
        "type",
        "subtype",
        "is_nullable",
        "constraint_name",
        "constraint_type",
        "references",
    ]
    return [dict(zip(column_names, result)) for result in results]


@router.put("/approve/{database_name}", response_model=schemas.Msg)
def approve_database(
    database_name: str,
    db: Session = Depends(deps.get_main_db),
    crud: CRUDInterface = Depends(deps.get_main_crud),
    current_user=Depends(deps.get_main_current_active_superuser),
):
    db_obj = crud.molar_database.get_by_database_name(db, database_name=database_name)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Database request not found!")

    crud.molar_database.approve(db, db_obj=db_obj)
    alembic_config = alembic_utils.get_alembic_config()
    try:
        install.install_molar_database(
            alembic_config=alembic_config,
            hostname=settings.POSTGRES_SERVER,
            postgres_username=settings.POSTGRES_USER,
            postgres_password=settings.POSTGRES_PASSWORD,
            new_database_name=db_obj.database_name,
            superuser_fullname=db_obj.superuser_fullname,
            superuser_email=db_obj.superuser_email,
            superuser_hashed_password=db_obj.superuser_password,
            revisions=db_obj.alembic_revisions,
        )
    except alembic.util.exc.CommandError as err:
        raise HTTPException(
            status_code=400,
            detail=f"There was an issue during the alembic migration: {str(err)}",
        )
    except sqlalchemy.exc.ProgrammingError as err:
        raise HTTPException(status_code=400, detail="Database already exists!")

    if settings.EMAILS_ENABLED:
        send_database_created_email(
            email_to=db_obj.superuser_email, database=db_obj.database_name
        )
    return {"msg": f"Database {database_name} created."}


@router.delete("/request/{database_name}", response_model=schemas.Msg)
def remove_database_requests(
    database_name: str,
    db: Session = Depends(deps.get_main_db),
    crud: CRUDInterface = Depends(deps.get_main_crud),
    crud_user=Depends(deps.get_main_current_active_superuser),
):
    db_obj = crud.molar_database.get_by_database_name(db, database_name=database_name)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Database request not found!")
    if db_obj.is_approved:
        raise HTTPException(
            status_code=403,
            detail="This database request has been approved and therefore cannot be removed",
        )
    crud.molar_database.remove(db, id=db_obj.id)
    return {"msg": "Database request removed"}


@router.delete("/{database_name}", response_model=schemas.Msg)
def remove_a_database(
    database_name: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_main_db),
    crud: CRUDInterface = Depends(deps.get_main_crud),
    crud_user=Depends(deps.get_main_current_active_superuser),
):
    db_obj = crud.molar_database.get_by_database_name(db, database_name=database_name)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Database not found!")
    crud.molar_database.remove_by_database_name(db, database_name=database_name)

    database.close_database(database_name)

    background_tasks.add_task(
        install.drop_database,
        hostname=settings.POSTGRES_SERVER,
        postgres_username=settings.POSTGRES_USER,
        postgres_password=settings.POSTGRES_PASSWORD,
        database=database_name,
    )
    return {"msg": "The database has been scheduled for deletion!"}
