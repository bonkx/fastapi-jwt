# Defines dependencies used by the routers

from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .core.config import Settings
from .core.database import get_session

DBSessionDep = Annotated[AsyncSession, Depends(get_session)]


@lru_cache
def get_settings():
    return Settings()
