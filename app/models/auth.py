
from pydantic import EmailStr, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import Self

from ..core.config import settings


class TokenSchema(SQLModel):
    detail: str | None = "Login successful"
    token_type: str = settings.TOKEN_TYPE
    access_token: str
    access_token_expire_in: str = f"{(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)}"  # multiply minute to 60s
    refresh_token: str
    refresh_token_expire_in: str = f"{(settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)}"  # multiply day to 86400s
    user: dict | None = None


class UserLoginModel(SQLModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "johndoe123@fastapi.com",
                "password": "testpass123",
            }
        }
    }


class PasswordResetRequestModel(SQLModel):
    email: EmailStr


class PasswordResetConfirmModel(SQLModel):
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)

    # @model_validator(mode='after')
    # def check_passwords_match(self) -> Self:
    #     if self.new_password != self.confirm_new_password:
    #         raise ValueError('Passwords did not match')
    #     return self

    @field_validator('confirm_new_password', mode='after')
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data['new_password']:
            raise ValueError('Passwords did not match')
        return value
