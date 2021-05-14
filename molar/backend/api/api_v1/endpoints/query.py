from typing import Any, Dict, List, Optional, Union

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from molar.backend import schemas
from molar.backend.api import deps
from molar.backend.database.query import query_builder
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{database_name}", response_model=List[Dict[str, Any]])
def query(
    database_name: str,
    types: Union[str, List[str]],
    limit: int = 10,
    offset: int = 0,
    joins: Optional[Union[List[schemas.QueryJoin], schemas.QueryJoin]] = None,
    filters: Optional[Union[schemas.QueryFilter, schemas.QueryFilterList]] = None,
    db: Session = Depends(deps.get_db),
    models=Depends(deps.get_models),
    current_user=Depends(deps.get_current_active_user),
    order_by: Optional[Union[str, List[str]]] = None,
):
    if db is None:
        raise HTTPException(status_code=404, detail="Database not found!")
    try:
        query = query_builder(
            db, models, types, limit, offset, joins, filters, order_by
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return query
