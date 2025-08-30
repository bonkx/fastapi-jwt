from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..repositories.hero_repo import HeroRepository
from ..schemas.hero_schema import HeroSchema, HeroCreateSchema, HeroUpdateSchema
from ..services.hero_service import HeroService
from ..utils.pagination import CustomPage

router = APIRouter()


async def get_service(session: AsyncSession = Depends(get_session)) -> HeroService:
    repo = HeroRepository(session)
    return HeroService(repo)


@router.get("/", response_model=CustomPage[HeroSchema])
async def read_heroes(
    search: Optional[str] = Query(None, description="Search by name or secret_name", ),
    sorting: Optional[str] = Query(None, description="Sort by Model field e.g. id:desc or name:asc", ),
    srv: HeroService = Depends(get_service)
):
    return await srv.list(search=search, sorting=sorting)


@router.get("/{id}", response_model=HeroSchema)
async def get_hero(
    id: int,
    srv: HeroService = Depends(get_service)
):
    return await srv.get_by_id(id)


@router.post("/", response_model=HeroSchema, status_code=status.HTTP_201_CREATED)
async def create_hero(
    hero: HeroCreateSchema,
    srv: HeroService = Depends(get_service)
):
    return await srv.create(hero)


@router.put("/{id}", response_model=HeroSchema)
async def update_hero(
    id: int,
    hero: HeroUpdateSchema,
    srv: HeroService = Depends(get_service)
):
    return await srv.edit(id=id, obj=hero)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hero(
    id: int,
    srv: HeroService = Depends(get_service)
):
    return await srv.delete(id)
