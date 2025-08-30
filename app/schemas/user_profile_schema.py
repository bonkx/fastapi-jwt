from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..core.config import settings
from ..utils.partial import optional
from ..models.base import BaseModel
from ..models.status import Status


class UserProfileCreateSchema(SQLModel):
    phone: str | None = None
    role: str | None = None
    birthday: date | None = None

    user_id: int
    status_id: int


@optional()
class UserProfileUpdateSchema(SQLModel):
    phone: str
    birthday: date


class UserProfilePhotoUpdateSchema(SQLModel):
    photo: str


class UserProfileSchema(UserProfileCreateSchema, BaseModel):
    photo: str | None = None
    user_id: int | None = Field(exclude=True)
    status_id: int | None = Field(exclude=True)
    status: Status | None = None

    @field_validator('photo')
    def make_photo(cls, v: str):
        return f"{settings.DOMAIN}/{v}" if v else None
