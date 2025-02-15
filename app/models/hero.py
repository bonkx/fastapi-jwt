
from typing import Annotated, List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel
from .hero_publisher import HeroPublisher, HeroPublisherSchema


class Hero(BaseModel, table=True):
    __tablename__ = 'hero'

    name: str = Field(index=True)
    age: int | None
    secret_name: str = Field(default=None, index=True)

    hero_publisher_id: int | None = Field(default=None, foreign_key="hero_publisher.id", ondelete="CASCADE")
    hero_publisher: HeroPublisher | None = Relationship(
        back_populates="heroes",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class HeroCreate(SQLModel):
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
class HeroUpdate(HeroCreate):
    pass


class HeroSchema(HeroCreate, BaseModel):
    hero_publisher_id: Annotated[int, Field(exclude=True)]  # exlude/hide field from response schema
    hero_publisher: HeroPublisher | None = None
