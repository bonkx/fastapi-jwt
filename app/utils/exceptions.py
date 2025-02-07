# global exceptions

from sqlalchemy.orm import DeclarativeBase


class NotFoundError(Exception):
    pass


class Base(DeclarativeBase):
    pass
