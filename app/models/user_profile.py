from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel
from .status import Status

if TYPE_CHECKING:
    from .users import User  # pragma: no cover


class UserProfile(BaseModel, table=True):
    __tablename__ = 'user_profile'

    phone: str | None = None
    photo: str | None = None
    role: str | None = None
    birthday: date | None = None

    user_id: int | None = Field(default=None, foreign_key="users.id", ondelete="CASCADE")
    user: "User" = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    status_id: int | None = Field(default=None, foreign_key="status.id", ondelete="CASCADE")
    status: Status = Relationship(
        back_populates="user_profiles",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserProfileCreate(SQLModel):
    phone: str | None = None
    photo: str | None = None
    role: str | None = None
    birthday: date | None = None

    user_id: int
    status_id: int


@optional()
class UserProfileUpdate(SQLModel):
    phone: str | None = None
    photo: str | None = None
    birthday: date | None = None


class UserProfileSchema(UserProfileCreate, BaseModel):
    user_id: int | None = Field(exclude=True)
    status_id: int | None = Field(exclude=True)
    status: Status | None = None
