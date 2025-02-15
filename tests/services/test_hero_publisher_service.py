from typing import List, Optional

from fastapi_pagination import Page, add_pagination, paginate

from app.models import HeroPublisher, HeroPublisherCreate, HeroPublisherUpdate
from app.services.hero_publisher_service import HeroPublisherService
from app.utils.exceptions import ResponseException

from . import pytest, pytestmark


async def test_add(db_session, payload_hero_publisher):
    response = await HeroPublisherService(db_session).create(payload_hero_publisher)
    data = response
    print(data)

    assert data.id == payload_hero_publisher["id"]
    assert data.name == "Marvel Comics"


async def test_get(db_session, payload_hero_publisher):
    # MOCK create data using Service
    created = await HeroPublisherService(db_session).create(payload_hero_publisher)

    response = await HeroPublisherService(db_session).get_by_id(id=created.id)
    data = response
    print(data)

    assert data.id == created.id
    assert data.name == "Marvel Comics"


async def test_edit(db_session, payload_hero_publisher, payload_hero_publisher_update):
    # MOCK create data using Service
    created = await HeroPublisherService(db_session).create(payload_hero_publisher)

    response = await HeroPublisherService(db_session).edit(id=created.id, obj=HeroPublisherUpdate(**payload_hero_publisher_update))
    data = response
    print(data)

    assert data.id == created.id
    assert data.name == "Marvel Comics Update"


async def test_delete(db_session, payload_hero_publisher):
    # MOCK create data using Service
    created = await HeroPublisherService(db_session).create(payload_hero_publisher)

    # delete data
    await HeroPublisherService(db_session).delete(id=created.id)

    # test get data
    with pytest.raises(ResponseException) as exc:
        await HeroPublisherService(db_session).get_by_id(id=created.id)

    assert exc.type == ResponseException
    assert exc.value.status_code == 404
    assert str(exc.value.detail) == f"Data with ID {created.id} not found"
