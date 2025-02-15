from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..models import UserSchema
from ..services.user_service import UserService

router = APIRouter()


@router.get("/{id}", response_model=UserSchema)
async def get_user(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    return await UserService(session).get_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    return await UserService(session).delete(id)
