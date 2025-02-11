# Defines functions for validation.

from fastapi import status

from ..utils.exceptions import ResponseException


def formatSorting(model, sorting):
    try:
        x = sorting.split(":")

        if not hasattr(model, x[0]):
            raise Exception()

        # print(x[0])
        # print(x[1])
        if (x[1].lower() == 'desc'):
            xSort = f"{x[0]} desc"
        else:
            xSort = f"{x[0]} asc"

        return xSort
    except Exception as e:
        raise ResponseException(
            detail="Sorting formatted incorrectly",
            status_code=status.HTTP_400_BAD_REQUEST,
            resolution="Try e.g. field_name:ASC or field_name:desc"
        )
