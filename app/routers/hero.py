from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, Session, SQLModel, create_engine, select

from ..configs.database import get_session
from ..dependencies import get_hero_service
from ..models.hero import Hero, HeroCreate
from ..services.hero_service import HeroService

router = APIRouter(
    prefix="/heroes",
    tags=["heroes"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[Hero])
async def read_heroes(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    return await HeroService(session).list(limit, offset)


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
