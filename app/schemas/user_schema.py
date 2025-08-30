from datetime import datetime
from typing import Annotated, Any, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from ..models.base import BaseModel
from ..schemas.user_profile_schema import UserProfileSchema, UserProfileUpdateSchema


class UserCreateSchema(SQLModel):
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
class UserUpdateSchema(SQLModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)

    profile: UserProfileUpdateSchema


class UserSchema(UserCreateSchema, BaseModel):
    password: str | None = Field(exclude=True)
    is_verified: bool
    is_superuser: bool
    is_staff: bool
    last_login_at: datetime | None = None
    last_login_ip: datetime | None = None
    verified_at: datetime | None = None

    profile: UserProfileSchema | None = None
