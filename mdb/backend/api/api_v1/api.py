from fastapi import APIRouter

from .endpoints import login, utils

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
