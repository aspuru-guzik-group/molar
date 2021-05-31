# external
from fastapi import APIRouter

from .endpoints import alembic, database, eventstore, login, query, user, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(database.router, prefix="/database", tags=["database"])
api_router.include_router(user.router, prefix="/user", tags=["users"])
api_router.include_router(alembic.router, prefix="/alembic", tags=["database"])
api_router.include_router(eventstore.router, prefix="/eventstore", tags=["eventstore"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
