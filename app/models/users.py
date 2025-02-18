from datetime import datetime
from typing import Annotated, Any, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel
from .user_profile import UserProfile, UserProfileSchema, UserProfileUpdate


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
    verified_at: datetime | None = None

    profile: "UserProfile" = Relationship(
        back_populates="user", cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


class UserCreate(SQLModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str = Field(max_length=20)
    email: EmailStr = Field(max_length=50)
    password: str = Field(min_length=4)

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "johndoe123@fastapi.com",
                "password": "testpass123",
            }
        }
    }


@optional()
class UserUpdate(SQLModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)

    profile: UserProfileUpdate


class UserSchema(UserCreate, BaseModel):
    password: str | None = Field(exclude=True)
    is_verified: bool
    is_superuser: bool
    is_staff: bool
    last_login_at: datetime | None = None
    last_login_ip: datetime | None = None
    verified_at: datetime | None = None

    profile: UserProfileSchema | None = None
