from typing import Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class ResponseSchema(BaseModel):
    detail: Optional[str] = "Request has been processed successfully"
    result: Optional[T] = None
