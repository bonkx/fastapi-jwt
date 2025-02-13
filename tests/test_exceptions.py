from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.database import DatabaseSessionManager
from app.models import Hero
from app.repositories import HeroRepository
from app.services import HeroService
from app.utils.exceptions import ResponseException

from . import pytest, pytestmark


async def test_session_exception(db_session, sessionmanager, payload_hero):

    async with sessionmanager.connect() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    with pytest.raises(OperationalError)as exc:
        await HeroService(db_session).create(payload_hero)

    assert exc.type == OperationalError


async def test_http_exception_500():

    with pytest.raises(Exception)as exc:
        raise HTTPException(status_code=500, detail="your detail")

    print(exc)
    assert exc.type == HTTPException
    assert exc.value.status_code == 500
