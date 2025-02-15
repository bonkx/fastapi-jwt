
from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel


class UserLoginModel(SQLModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class PasswordResetRequestModel(SQLModel):
    email: EmailStr


class PasswordResetConfirmModel(SQLModel):
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)
