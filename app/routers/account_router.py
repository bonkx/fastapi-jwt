import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import Settings
from ..core.database import get_session
from ..core.security import decode_token
from ..dependencies import AccessTokenBearer, CurrentUser, get_settings
from ..repositories.user_repo import UserRepository
from ..schemas.user_schema import UserSchema, UserUpdateSchema
from ..services.user_service import UserService
from ..utils.file import upload_image, upload_image_crop

router = APIRouter(
    dependencies=[Depends(AccessTokenBearer())]
)


async def get_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


@router.get("/me", response_model=UserSchema)
async def get_profile(
    user: CurrentUser,
):
    return user


@router.patch("/update", response_model=UserSchema)
async def update_profile(
    payload: UserUpdateSchema,
    user: CurrentUser,
    srv: UserService = Depends(get_service)
):
    return await srv.update_profile(user, payload)


@router.post("/photo", response_model=UserSchema)
async def upload_photo_profile(
    file: UploadFile,
    user: CurrentUser,
    srv: UserService = Depends(get_service)
):
    try:
        file_name = await upload_image_crop(file)

        # update photo of user
        return await srv.update_photo_profile(user, file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
