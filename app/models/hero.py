from typing import Annotated, Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from ..utils.partial import optional
from .base import BaseModel


class Hero(BaseModel, table=True):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


class HeroCreate(SQLModel):
    name: str
    age: int
    secret_name: str

    @field_validator("age")
    def check_age(cls, value):
        if value < 0:
            raise ValueError("Invalid age")
        return value


@optional()
class HeroUpdate(HeroCreate):
    pass
