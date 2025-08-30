from fastapi import APIRouter, Depends

from ..core.config import settings
from ..core.database import get_session
from ..dependencies import AccessTokenBearer, RoleChecker

from . import users_router

admin_role_checker = Depends(RoleChecker(["ADMIN"]))
token_middleware = Depends(AccessTokenBearer())


router = APIRouter(
    dependencies=[token_middleware, admin_role_checker]
)


router.include_router(users_router.router, prefix=f"{settings.API_PREFIX}/users", tags=["admin"])

# @router.post("/")
# async def update_admin():
#     return {"detail": "Admin getting schwifty"}
