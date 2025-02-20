from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.security import decode_token
from ..dependencies import AccessTokenBearer, get_current_user
from ..models import UserSchema, UserUpdate
from ..services.user_service import UserService

router = APIRouter(
    dependencies=[Depends(AccessTokenBearer())]
)


@router.get("/me", response_model=UserSchema)
async def get_profile(
    user: Annotated[UserSchema, Depends(get_current_user)],
):
    return user


@router.patch("/update", response_model=UserSchema)
async def update_profile(
    payload: UserUpdate,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    return await UserService(session).update_profile(user, payload)


# @router.get("/users/{username}", tags=["users"])
# async def read_user(username: str):
#     return {"username": username}
