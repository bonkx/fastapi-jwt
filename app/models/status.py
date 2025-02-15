from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

from ..utils.partial import optional
from .base import BaseModel


class Status(BaseModel, table=True):
    __tablename__ = 'status'

    name: str = Field(index=True, unique=True)
