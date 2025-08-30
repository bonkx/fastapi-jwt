
from typing import Annotated, List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from ..models import BaseModel, HeroPublisher


class HeroCreateSchema(SQLModel):
    name: str
    age: int
    secret_name: str
    hero_publisher_id: int

    @field_validator("age")
    def check_age(cls, value):
        if value < 0:
            raise ValueError("Invalid age")
        return value


@optional()
class HeroUpdateSchema(HeroCreateSchema):
    pass


class HeroSchema(HeroCreateSchema, BaseModel):
    hero_publisher_id: Annotated[int, Field(exclude=True)]  # exlude/hide field from response schema
    hero_publisher: HeroPublisher | None = None
