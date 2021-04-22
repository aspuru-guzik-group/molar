from datetime import datetime

from fastapi import APIRouter

from .... import database, schemas

router = APIRouter()


@router.post("/database/create_request", response_model=schemas.Msg)
def database_creation_request(database_name: str, superuser_email: str):
    db = database.main.get_session()
    request = database.main.models.molar_database(
        database_name=database_name,
        superuser_email=superuser_email,
        request_time=datetime.utcnow(),
        is_created=False,
    )
    db.add(request)
    db.commit()


@router.get("/database_requests")
def get_database_requests():
    db = database.main.get_session()
    db.query(database.main.molar_database).fetchall()
