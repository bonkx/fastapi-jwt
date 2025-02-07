# Defines dependencies used by the routers

from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

from .configs.database import SessionDep, get_session
from .configs.env import Settings
from .repositories.hero_repo import HeroRepository, IHeroRepository
from .services.hero_service import HeroService


@lru_cache
def get_settings():
    return Settings()


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def get_hero_service() -> HeroService:
    """Dependency injection to get the service."""
    repo = HeroRepository(db=SessionDep)
    return HeroService(repository=repo)
