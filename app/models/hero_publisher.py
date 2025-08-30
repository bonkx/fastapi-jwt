from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import BaseModel, field_validator
from sqlmodel import Field, Relationship, SQLModel

from .base import BaseModel

if TYPE_CHECKING:
    from .hero import Hero  # pragma: no cover


class HeroPublisher(BaseModel, table=True):
    __tablename__ = 'hero_publisher'

    name: str = Field(index=True)

    heroes: List["Hero"] = Relationship(
        back_populates="hero_publisher", cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"}
    )
