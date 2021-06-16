# std
from typing import Any, Dict, List, Optional, Union

# external
from fastapi import APIRouter, Depends, HTTPException
import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

# molar
from molar.backend import schemas
from molar.backend.api import deps
from molar.backend.database.query import process_query_output, query_builder

router = APIRouter()


@router.get("/{database_name}", response_model=List[Dict[str, Any]])
def query(
    database_name: str,
    types: schemas.QueryTypes,
    limit: int = 10,
    offset: int = 0,
    joins: Optional[schemas.QueryJoins] = None,
    filters: Optional[schemas.QueryFilters] = None,
    aliases: Optional[schemas.QueryAliases] = None,
    db: Session = Depends(deps.get_db),
    models=Depends(deps.get_models),
    current_user=Depends(deps.get_current_active_user),
    order_by: Optional[schemas.QueryOrderBys] = None,
):
    if db is None:
        raise HTTPException(status_code=404, detail="Database not found!")
    try:
        query, db_objs, types = query_builder(
            db, models, types, limit, offset, joins, filters, order_by, aliases
        )
        records = process_query_output(db_objs, query.all(), types)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    except sqlalchemy.exc.AmbiguousForeignKeysError as err:
        raise HTTPException(status_code=400, detail=str(err))

    except sqlalchemy.exc.ProgrammingError as err:
        if "specified more than once":
            raise HTTPException(
                status_code=400,
                detail="A field is specified more than once in the query!",
            )
        raise HTTPException(status_code=400, detail=str(err))
    return records


@router.get("/debug/{database_name}", response_model=str)
def debug_query(
    database_name: str,
    types: schemas.QueryTypes,
    limit: int = 10,
    offset: int = 0,
    joins: Optional[schemas.QueryJoins] = None,
    fitlers: Optional[schemas.QueryFilters] = None,
    aliases: Optional[schemas.QueryAliases] = None,
    db: Session = Depends(deps.get_db),
    models=Depends(deps.get_models),
    current_user=Depends(deps.get_current_active_user),
    order_by: Optional[schemas.QueryOrderBys] = None,
    explain_analyze: bool = False,
):
    if db is None:
        raise HTTPException(status_code=404, detail="Database not found!")

    query, _, _ = query_builder(
        db, models, types, limit, offset, joins, fitlers, order_by, aliases
    )
    statement = str(
        query.statement.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )
    if not explain_analyze:
        return statement

    statement = f"explain analyze {statement}"
    result = db.execute(statement)
    return "\n".join([res[0] for res in result.all()])
