
from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel


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
