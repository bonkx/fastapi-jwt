from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel

if TYPE_CHECKING:
    from .user_profile import UserProfile


class Status(BaseModel, table=True):
    __tablename__ = 'status'

    name: str = Field(index=True, unique=True)

    user_profiles: List["UserProfile"] = Relationship(
        back_populates="status", cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"}
    )
