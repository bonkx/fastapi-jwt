from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..repositories.user_repo import UserRepository
from ..schemas.user_schema import UserSchema
from ..services.user_service import UserService
from ..utils.pagination import CustomPage

router = APIRouter()


async def get_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


@router.get("/", response_model=CustomPage[UserSchema])
async def read_users(
    search: Optional[str] = Query(None, description="Search by name or secret_name", ),
    sorting: Optional[str] = Query(None, description="Sort by Model field e.g. id:desc or name:asc", ),
    srv: UserService = Depends(get_service)
):
    return await srv.list(search=search, sorting=sorting)


@router.get("/{id}", response_model=UserSchema)
async def get_user(
    id: int,
    srv: UserService = Depends(get_service)
):
    return await srv.get_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    srv: UserService = Depends(get_service)
):
    return await srv.delete(id)
