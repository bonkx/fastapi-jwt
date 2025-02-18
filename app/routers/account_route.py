from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.security import decode_token
from ..dependencies import AccessTokenBearer, get_current_user
from ..models import UserSchema

router = APIRouter(
    dependencies=[Depends(AccessTokenBearer())]
)


@router.get("/me")
async def get_profile(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
):
    return UserSchema.model_validate(current_user)


# @router.get("/users/me", tags=["users"])
# async def read_user_me():
#     return {"username": "fakecurrentuser"}


# @router.get("/users/{username}", tags=["users"])
# async def read_user(username: str):
#     return {"username": username}
