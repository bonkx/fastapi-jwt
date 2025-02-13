from typing import List, Optional

from fastapi_pagination import Page, add_pagination, paginate

from app.models import Hero, HeroCreate, HeroUpdate
from app.services import HeroService
from app.utils.exceptions import ResponseException

from . import pytest, pytestmark


async def test_add(db_session, payload_hero):
    response = await HeroService(db_session).create(payload_hero)
    data = response
    print(data)

    assert data.name == "Tony Stark"
    assert data.secret_name == "Iron Man"
    assert data.age == 40
    assert data.hero_publisher_id == payload_hero["hero_publisher_id"]


async def test_get(db_session, payload_hero):
    # MOCK create hero using Service
    created = await HeroService(db_session).create(payload_hero)

    response = await HeroService(db_session).get_by_id(id=created.id)
    data = response
    print(data)

    assert data.name == "Tony Stark"
    assert data.secret_name == "Iron Man"
    assert data.age == 40
    assert data.id == payload_hero["id"]
    assert data.hero_publisher_id == payload_hero["hero_publisher_id"]


async def test_edit(db_session, payload_hero, payload_hero_update):
    # MOCK create hero using Service
    created = await HeroService(db_session).create(payload_hero)

    response = await HeroService(db_session).edit(id=created.id, obj=HeroUpdate(**payload_hero_update))
    data = response
    print(data)

    assert data.name == "Tony Stark Update"
    assert data.secret_name == "Iron Man Update"
    assert data.age == 30
    assert data.id == payload_hero["id"]
    assert data.hero_publisher_id == payload_hero["hero_publisher_id"]


async def test_delete(db_session, payload_hero):
    # MOCK create hero using Service
    created = await HeroService(db_session).create(payload_hero)

    await HeroService(db_session).delete(id=created.id)

    with pytest.raises(ResponseException) as exc:
        await HeroService(db_session).get_by_id(id=created.id)

    assert exc.type == ResponseException
    assert exc.value.status_code == 404
    assert str(exc.value.detail) == f"Hero with ID {created.id} not found"
