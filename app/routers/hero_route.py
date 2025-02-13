from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..models import Hero, HeroCreate, HeroSchema, HeroUpdate
from ..services.hero_service import HeroService
from ..utils.pagination import CustomPage

# router = APIRouter(
#     prefix="/heroes",
#     tags=["heroes"],
#     responses={404: {"description": "Not found"}},
# )
router = APIRouter()


@router.get("/", response_model=CustomPage[HeroSchema])
async def read_heroes(
    search: Optional[str] = Query(None, description="Search by name or secret_name", ),
    sorting: Optional[str] = Query(None, description="Sort by Model field e.g. id:desc or name:asc", ),
    session: AsyncSession = Depends(get_session),
):
    return await HeroService(session).list(search=search, sorting=sorting)


@router.get("/{id}", response_model=HeroSchema)
async def get_hero(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    return await HeroService(session).get_by_id(id)


@router.post("/", response_model=HeroSchema, status_code=status.HTTP_201_CREATED)
async def create_hero(
    hero: HeroCreate,
    session: AsyncSession = Depends(get_session),
):
    return await HeroService(session).create(hero)


@router.put("/{id}", response_model=HeroSchema)
async def update_hero(
    id: int,
    hero: HeroUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await HeroService(session).edit(id=id, obj=hero)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hero(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    return await HeroService(session).delete(id)
