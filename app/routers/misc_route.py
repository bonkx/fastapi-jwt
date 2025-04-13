import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import settings
from ..core.database import get_session
from ..dependencies import AccessTokenBearer, get_current_user
from ..models import UserSchema
from ..utils.file import upload_image

upload_router = APIRouter(
    dependencies=[Depends(AccessTokenBearer())]
)


@upload_router.post("/image")
async def upload_image_file(
    file: UploadFile,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
):
    try:
        file_name = await upload_image(file)

        return JSONResponse(
            content={
                "detail": "Upload image Successfully",
                "file_name": f"{settings.DOMAIN}/{file_name}",
            }, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
