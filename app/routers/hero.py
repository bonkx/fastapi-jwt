from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, Session, SQLModel, create_engine, select

from ..configs.database import get_session
from ..models.hero import Hero, HeroCreate
from ..services.hero_service import HeroService
from ..utils.pagination import CustomPage

# router = APIRouter(
#     prefix="/heroes",
#     tags=["heroes"],
#     responses={404: {"description": "Not found"}},
# )
router = APIRouter()


@router.get("/", response_model=CustomPage[Hero])
async def read_heroes(
    search: Optional[str] = None,
    sorting: Optional[str] = None,
    session: Session = Depends(get_session),
):
    return await HeroService(session).list(search=search, sorting=sorting)


@router.get("/{id}", response_model=Hero)
async def get_hero(
    id: int,
    session: Session = Depends(get_session),
):
    return await HeroService(session).get_by_id(id)


@router.post("/", response_model=Hero, status_code=status.HTTP_201_CREATED)
async def create_hero(
    hero: HeroCreate,
    session: Session = Depends(get_session),
):
    return await HeroService(session).add(hero)
