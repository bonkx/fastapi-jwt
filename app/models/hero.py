from typing import Annotated, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel


class HeroPublisher(BaseModel, table=True):
    __tablename__ = 'hero_publisher'

    name: str = Field(index=True)

    heroes: list["Hero"] = Relationship(back_populates="hero_publisher", cascade_delete=True)
    # parents: list['Node'] = Relationship(back_populates="child", link_model=ParentChildLinkTable)


class HeroPublisherCreate(SQLModel):
    name: str


@optional()
class HeroPublisherUpdate(HeroPublisherCreate):
    pass


class Hero(BaseModel, table=True):
    # __tablename__ = 'hero'

    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str

    hero_publisher_id: int | None = Field(default=None, foreign_key="hero_publisher.id", ondelete="CASCADE")
    hero_publisher: HeroPublisher | None = Relationship(back_populates="heroes")


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
