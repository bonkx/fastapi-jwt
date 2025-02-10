from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, Session, SQLModel, create_engine, select

from ..core.database import get_session
from ..models.hero import Hero, HeroCreate, HeroUpdate
from ..services.hero_service import HeroService
from ..utils.pagination import CustomPage
from ..utils.response import IGetResponseBase, create_response

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


@router.put("/{id}", response_model=Hero)
async def update_hero(
    id: int,
    hero: HeroUpdate,
    session: Session = Depends(get_session),
):
    return await HeroService(session).edit(id=id, obj=hero)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hero(
    id: int,
    session: Session = Depends(get_session),
):
    return await HeroService(session).delete(id)
