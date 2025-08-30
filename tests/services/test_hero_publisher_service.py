from typing import List, Optional

from fastapi_pagination import Page, add_pagination, paginate

from app.models import HeroPublisher
from app.schemas.hero_publisher_schema import HeroPublisherCreateSchema, HeroPublisherUpdateSchema
from app.services.hero_publisher_service import HeroPublisherService
from app.repositories.hero_publisher_repo import HeroPublisherRepository
from app.utils.exceptions import ResponseException

from . import pytest, pytestmark


class TestHeroPublisherService:
    @pytest.fixture(autouse=True)
    def init(self, client, api_prefix, db_session, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.repo = HeroPublisherRepository(self.db_session)
        self.srv = HeroPublisherService(self.repo)

    async def test_add(self):
        response = await self.srv.create(HeroPublisherCreateSchema(**self.payload_hero_publisher))
        data = response
        print(data)

        assert data.id == self.payload_hero_publisher["id"]
        assert data.name == "Marvel Comics"

    async def test_get(self):
        # MOCK create data using Service
        created = await self.srv.create(HeroPublisherCreateSchema(**self.payload_hero_publisher))

        response = await self.srv.get_by_id(id=created.id)
        data = response
        print(data)

        assert data.id == created.id
        assert data.name == "Marvel Comics"

    async def test_edit(self):
        # MOCK create data using Service
        created = await self.srv.create(HeroPublisherCreateSchema(**self.payload_hero_publisher))

        response = await self.srv.edit(id=created.id, obj=HeroPublisherUpdateSchema(**self.payload_hero_publisher_update))
        data = response
        print(data)

        assert data.id == created.id
        assert data.name == "Marvel Comics Update"

    async def test_delete(self):
        # MOCK create data using Service
        created = await self.srv.create(HeroPublisherCreateSchema(**self.payload_hero_publisher))

        # delete data
        await self.srv.delete(id=created.id)

        # test get data
        with pytest.raises(ResponseException) as exc:
            await self.srv.get_by_id(id=created.id)

        assert exc.type == ResponseException
        assert exc.value.status_code == 404
        assert str(exc.value.detail) == f"Data with ID {created.id} not found"
