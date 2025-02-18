
from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

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

    @field_validator("confirm_new_password")
    def verify_password_match(cls, v, values, **kwargs):
        password = values.get("new_password")

        if v != password:
            raise ValueError("The two passwords did not match.")

        return v
