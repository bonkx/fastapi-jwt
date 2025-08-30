from datetime import datetime
from typing import Annotated, Any, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

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
    verified_at: datetime | None = None

    profile: "UserProfile" = Relationship(
        back_populates="user", cascade_delete=True,
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
