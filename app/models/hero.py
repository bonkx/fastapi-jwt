
from typing import Annotated, List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from .base import BaseModel
from .hero_publisher import HeroPublisher


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
