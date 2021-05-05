from fastapi import APIRouter, Depends
from molar.backend.api import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{database_name}")
def view_eventstore(database_name: str, db: Session = Depends(deps.get_db)):
    pass


@router.post("/{database_name}")
def create(database_name: str, db: Session = Depends(deps.get_db)):
    pass


@router.patch("/{database_name}")
def update(database_name: str, db: Session = Depends(deps.get_db)):
    pass


@router.delete("/{database_name}")
def delete(database_name: str, db: Session = Depends(deps.get_db)):
    pass
