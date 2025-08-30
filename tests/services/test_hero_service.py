from typing import List, Optional

from fastapi_pagination import Page, add_pagination, paginate

from app.models import Hero
from app.schemas.hero_schema import HeroCreateSchema, HeroUpdateSchema
from app.services.hero_service import HeroService
from app.repositories.hero_repo import HeroRepository
from app.utils.exceptions import ResponseException

from . import pytest, pytestmark


class TestHeroService:
    @pytest.fixture(autouse=True)
    def init(self, client, api_prefix, db_session, payload_hero, payload_hero_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero = payload_hero
        self.payload_hero_update = payload_hero_update
        self.repo = HeroRepository(self.db_session)
        self.srv = HeroService(self.repo)

    async def test_add(self):
        response = await self.srv.create(HeroCreateSchema(**self.payload_hero))
        data = response

        assert data.name == "Tony Stark"
        assert data.secret_name == "Iron Man"
        assert data.age == 40
        assert data.hero_publisher_id == self.payload_hero["hero_publisher_id"]

    async def test_get(self):
        # MOCK create hero using Service
        created = await self.srv.create(HeroCreateSchema(**self.payload_hero))

        response = await self.srv.get_by_id(id=created.id)
        data = response

        assert data.name == "Tony Stark"
        assert data.secret_name == "Iron Man"
        assert data.age == 40
        assert data.id == self.payload_hero["id"]
        assert data.hero_publisher_id == self.payload_hero["hero_publisher_id"]

    async def test_edit(self):
        # MOCK create hero using Service
        created = await self.srv.create(HeroCreateSchema(**self.payload_hero))

        response = await self.srv.edit(id=created.id, obj=HeroUpdateSchema(**self.payload_hero_update))
        data = response

        assert data.name == "Tony Stark Update"
        assert data.secret_name == "Iron Man Update"
        assert data.age == 30
        assert data.id == self.payload_hero["id"]
        assert data.hero_publisher_id == self.payload_hero["hero_publisher_id"]

    async def test_delete(self):
        # MOCK create hero using Service
        created = await self.srv.create(HeroCreateSchema(**self.payload_hero))

        await self.srv.delete(id=created.id)

        with pytest.raises(ResponseException) as exc:
            await self.srv.get_by_id(id=created.id)

        assert exc.type == ResponseException
        assert exc.value.status_code == 404
        assert str(exc.value.detail) == f"Hero with ID {created.id} not found"
