from fastapi import APIRouter

from ..core.config import settings
from . import users

router = APIRouter()


router.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["Admin Users"])

# @router.post("/")
# async def update_admin():
#     return {"detail": "Admin getting schwifty"}
