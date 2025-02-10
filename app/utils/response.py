from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel

DataType = TypeVar("DataType")
T = TypeVar("T")


class IResponseBase(BaseModel, Generic[T]):
    detail: str = "Request has been processed successfully"
    meta: dict | Any | None = {}
    result: T | None = None


class IGetResponseBase(IResponseBase[DataType], Generic[DataType]):
    detail: str | None = "Data got correctly"


class IPostResponseBase(IResponseBase[DataType], Generic[DataType]):
    detail: str | None = "Data created correctly"


class IPutResponseBase(IResponseBase[DataType], Generic[DataType]):
    detail: str | None = "Data updated correctly"


class IDeleteResponseBase(IResponseBase[DataType], Generic[DataType]):
    detail: str | None = "Data deleted correctly"


def create_response(
    data: DataType,
    detail: str | None = None,
    meta: dict | Any | None = {},
) -> (
    IResponseBase[DataType]
    | IGetResponseBase[DataType]
    | IPutResponseBase[DataType]
    | IDeleteResponseBase[DataType]
    | IPostResponseBase[DataType]
):
    # res = {"result": data}
    # if detail:
    #     res["detail"] = detail
    # if meta:
    #     res["meta"] = meta

    return {"data": data, "detail": detail, "meta": meta}
