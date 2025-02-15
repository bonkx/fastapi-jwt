from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.database import DatabaseSessionManager
from app.models import Hero
from app.repositories.hero_publisher_repo import HeroPublisherRepository
from app.repositories.hero_repo import HeroRepository
from app.services.hero_service import HeroService
from app.utils.exceptions import ResponseException

from . import pytest, pytestmark


class TestExceptions:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, sessionmanager, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.sessionmanager = sessionmanager
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.url = f"{self.api_prefix}/hero-publishers/"

    async def test_db_exception(self):

        # drop the tables
        async with self.sessionmanager.connect() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        # get the data
        id = 1
        url = f"{self.url}{id}"

        with pytest.raises(OperationalError)as exc:
            await self.client.get(url)

        assert exc.type == OperationalError


async def test_http_exception_500():

    with pytest.raises(Exception)as exc:
        raise HTTPException(status_code=500, detail="your detail")

    print(exc)
    assert exc.type == HTTPException
    assert exc.value.status_code == 500
