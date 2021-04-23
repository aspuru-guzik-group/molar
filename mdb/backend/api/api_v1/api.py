from fastapi import APIRouter

from .endpoints import login, utils, user_manage

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(user_manage.router, prefix="/users", tags=["User Management"])
