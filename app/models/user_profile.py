from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel
from .status import Status

if TYPE_CHECKING:
    from .users import User


class UserProfile(BaseModel, table=True):
    __tablename__ = 'user_profile'

    phone: str | None = None
    photo: str | None = None
    role: str | None = None
    birthday: date | None = None

    user_id: int | None = Field(default=None, foreign_key="users.id", ondelete="CASCADE")
    user: Optional["User"] | None = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    status_id: int | None = Field(default=None, foreign_key="status.id", ondelete="CASCADE")
    status: Status | None = Relationship(
        back_populates="user_profiles",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
