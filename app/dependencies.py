# Defines dependencies used by the routers

from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends, Header
from sqlmodel import Field, Session, SQLModel, create_engine, select

from .core.config import Settings


@lru_cache
def get_settings():
    return Settings()
