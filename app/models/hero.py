from typing import Annotated, Optional

from sqlmodel import Field, SQLModel

from .base import BaseModel


class Hero(BaseModel, table=True):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


class HeroCreate(SQLModel):
    name: str
    age: int
    secret_name: str


class HeroUpdate(HeroCreate):
    name: Optional[str]
    age: Optional[int]
    secret_name: Optional[str]
