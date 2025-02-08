# global module e.g. pagination

from typing import Optional, TypeVar

from fastapi import Query
from fastapi_pagination.customization import (CustomizedPage,
                                              UseExcludedFields,
                                              UseFieldsAliases,
                                              UseIncludeTotal, UseName,
                                              UseParamsFields)
from fastapi_pagination.links import Page

T = TypeVar('T')

CustomPage = CustomizedPage[
    Page[T],
    UseName("CustomPage"),
    UseParamsFields(
        size=Query(10, ge=1, le=100),
        page=Query(1, ge=1),
    ),
    UseFieldsAliases(
        items="results",
    ),
]
