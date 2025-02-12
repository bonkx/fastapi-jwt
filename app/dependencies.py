# Defines dependencies used by the routers
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from .core.config import Settings
from .core.database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@lru_cache
def get_settings():
    return Settings()
