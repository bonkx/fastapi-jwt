from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import BaseModel, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from ..models import BaseModel, Hero


class HeroPublisherCreateSchema(SQLModel):
    name: str


@optional()
class HeroPublisherUpdateSchema(HeroPublisherCreateSchema):
    pass


class HeroPublisherSchema(HeroPublisherCreateSchema, BaseModel):
    pass


class ListHeroPublisherSchema(HeroPublisherCreateSchema, BaseModel):
    heroes: List[Hero] | None = None
