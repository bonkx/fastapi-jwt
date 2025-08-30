
from typing import Annotated, Any, Dict, List, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel


class EmailSchema(SQLModel):
    subject: str = "Email Subject"
    emails: List[EmailStr]
    body: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "example": {
                "subject": "Email Subject",
                "emails": [
                    "user@example.com"
                ],
                "body": {
                    "title": "Hello World",
                    "name": "John Doe"
                }
            }
        }
    }
