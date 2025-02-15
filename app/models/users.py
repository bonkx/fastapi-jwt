from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel
from .user_profile import UserProfile


class User(BaseModel, table=True):
    __tablename__ = 'users'

    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str

    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    last_login_at: datetime | None = None
    last_login_ip: datetime | None = None
    verification_code: str | None = None
    verified_at: datetime | None = None

    profile: Optional["UserProfile"] = Relationship(
        back_populates="user", cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserCreate(SQLModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


@optional()
class UserUpdate(SQLModel):
    pass


class UserSchema(UserCreate, BaseModel):
    pass
