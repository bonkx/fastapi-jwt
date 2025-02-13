from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..models import (HeroPublisher, HeroPublisherCreate, HeroPublisherSchema,
                      HeroPublisherUpdate)
from ..services.hero_publisher_service import HeroPublisherService
from ..utils.pagination import CustomPage

router = APIRouter()


@router.get("/", response_model=CustomPage[HeroPublisher])
async def read_data(
    search: Optional[str] = Query(None, description="Search by name or secret_name", ),
    sorting: Optional[str] = Query(None, description="Sort by Model field e.g. id:desc or name:asc", ),
    session: AsyncSession = Depends(get_session),
):
    return await HeroPublisherService(session).list(search=search, sorting=sorting)


@router.get("/{id}", response_model=HeroPublisher)
async def get_data(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    return await HeroPublisherService(session).get_by_id(id)


@router.post("/", response_model=HeroPublisher, status_code=status.HTTP_201_CREATED)
async def create_data(
    payload: HeroPublisherCreate,
    session: AsyncSession = Depends(get_session),
):
    return await HeroPublisherService(session).add(payload)


@router.put("/{id}", response_model=HeroPublisher)
async def update_data(
    id: int,
    payload: HeroPublisherUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await HeroPublisherService(session).edit(id=id, obj=payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    return await HeroPublisherService(session).delete(id)
