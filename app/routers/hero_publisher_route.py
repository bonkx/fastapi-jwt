from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..models import (HeroPublisher, HeroPublisherCreateSchema, HeroPublisherSchema,
                      HeroPublisherUpdateSchema)
from ..services.hero_publisher_service import HeroPublisherService
from ..repositories.hero_publisher_repo import HeroPublisherRepository
from ..utils.pagination import CustomPage

router = APIRouter()


async def get_service(session: AsyncSession = Depends(get_session)) -> HeroPublisherService:
    repo = HeroPublisherRepository(session)
    return HeroPublisherService(repo)


@router.get("/", response_model=CustomPage[HeroPublisher])
async def read_hero_publishers(
    search: Optional[str] = Query(None, description="Search by name or secret_name", ),
    sorting: Optional[str] = Query(None, description="Sort by Model field e.g. id:desc or name:asc", ),
    srv: HeroPublisherService = Depends(get_service)
):
    return await srv.list(search=search, sorting=sorting)


@router.get("/{id}", response_model=HeroPublisher)
async def get_hero_publisher(
    id: int,
    srv: HeroPublisherService = Depends(get_service)
):
    return await srv.get_by_id(id)


@router.post("/", response_model=HeroPublisher, status_code=status.HTTP_201_CREATED)
async def create_hero_publisher(
    payload: HeroPublisherCreateSchema,
    srv: HeroPublisherService = Depends(get_service)
):
    return await srv.create(payload)


@router.put("/{id}", response_model=HeroPublisher)
async def update_hero_publisher(
    id: int,
    payload: HeroPublisherUpdateSchema,
    srv: HeroPublisherService = Depends(get_service)
):
    return await srv.edit(id=id, obj=payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hero_publisher(
    id: int,
    srv: HeroPublisherService = Depends(get_service)
):
    return await srv.delete(id)
