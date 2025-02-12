# import time
import math
from random import randint

from faker import Faker
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.models import Hero, HeroCreate, HeroPublisher, HeroPublisherCreate
from app.repositories.hero_repo import HeroRepository

from . import pytest, pytestmark

fake = Faker()


#############################################
# Create
#############################################
async def test_create_heroes(client, api_prefix, db_session, payload_hero, payload_hero_publisher):
    # MOCK create hero_publisher using model
    hero_publisher = HeroPublisher(**payload_hero_publisher)
    db_session.add(hero_publisher)
    await db_session.commit()
    await db_session.refresh(hero_publisher)

    print(hero_publisher)
    print(hero_publisher.id)
    assert hero_publisher.id == payload_hero_publisher["id"]
    assert hero_publisher.name == payload_hero_publisher["name"]

    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json=payload_hero)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_201_CREATED
    assert data["name"] == "Tony Stark"
    assert data["secret_name"] == "Iron Man"
    assert data["age"] == 40
    assert data["hero_publisher_id"] == hero_publisher.id
    assert "id" in data


async def test_create_heroes_422_exception(client, api_prefix):
    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json={})
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["msg"] == "Field required"


async def test_create_heroes_validation(client, api_prefix, payload_hero):
    payload = payload_hero

    # TEST hero_publisher_id exception
    # set hero_publisher_id invalid value
    payload["hero_publisher_id"] = None

    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json=payload)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["type"] == "int_type"
    assert data["detail"][0]["loc"][1] == "hero_publisher_id"
    assert data["detail"][0]["msg"] == "Input should be a valid integer"

    # TEST age exception
    # set age invalid value
    payload["age"] = -1

    url = f"{api_prefix}/heroes/"
    response = await client.post(url, json=payload)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["type"] == "value_error"
    assert data["detail"][0]["loc"][1] == "age"
    assert data["detail"][0]["msg"] == "Value error, Invalid age"


#############################################
# Get
#############################################
async def test_get_hero(client, api_prefix, db_session, payload_hero):
    # MOCK create hero using Repo
    payload_hero["hero_publisher_id"] = 1
    hero = await HeroRepository(db_session).create(payload_hero)
    print(hero)

    id = hero.id

    url = f"{api_prefix}/heroes/{id}"
    response = await client.get(url)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_200_OK
    assert data["name"] == "Tony Stark"
    assert data["secret_name"] == "Iron Man"
    assert data["age"] == 40
    assert data["id"] == id
    assert data["hero_publisher_id"] == 1


async def test_get_hero_not_found(client, api_prefix):
    id = 2

    url = f"{api_prefix}/heroes/{id}"
    response = await client.get(url)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == f"Hero with ID {id} not found"


async def test_get_hero_count(db_session, payload_hero, payload_hero_update):
    # change value for sequence insert
    payload_hero_update["id"] = 2
    payload_hero_update["hero_publisher_id"] = 2

    # MOCK create multi hero using Repo
    response = await HeroRepository(db_session).add_all(
        [
            Hero(**payload_hero),
            Hero(**payload_hero_update),
        ]
    )
    assert len(response) == 2

    # get count heroes data
    response = await HeroRepository(db_session).get_count(select(Hero))

    assert response == 2


#############################################
# Update
#############################################
async def test_update_hero(client, api_prefix, db_session, payload_hero, payload_hero_update):
    # MOCK create hero using Repo
    hero = await HeroRepository(db_session).create(payload_hero)
    print(hero)

    id = hero.id

    url = f"{api_prefix}/heroes/{id}"
    response = await client.put(url, json=payload_hero_update)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_200_OK
    assert data["name"] == "Tony Stark Update"
    assert data["secret_name"] == "Iron Man Update"
    assert data["age"] == 30
    assert data["id"] == id


async def test_update_hero_wrong_payload(client, api_prefix, payload_hero_update):
    id = payload_hero_update['id']

    payload_hero_update["name"] = (
        True  # name should be a string not a boolean
    )

    url = f"{api_prefix}/heroes/{id}"
    response = await client.put(url, json=payload_hero_update)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data == {
        "detail": [
            {
                "type": "string_type",
                "loc": ["body", "name"],
                "msg": "Input should be a valid string",
                "input": True,
            }
        ]
    }


async def test_update_hero_not_found(client, api_prefix, payload_hero_update):
    id = 2
    url = f"{api_prefix}/heroes/{id}"

    response = await client.put(url, json=payload_hero_update)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == f"Hero with ID {id} not found"


#############################################
# Delete
#############################################
async def test_delete_hero(client, api_prefix, db_session, payload_hero):
    # MOCK create hero using Repo
    hero = await HeroRepository(db_session).create(payload_hero)
    print(hero)

    id = hero.id

    url = f"{api_prefix}/heroes/{id}"
    response = await client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ""

    # Try to get the deleted item
    response = await client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


#############################################
# List
#############################################
async def test_read_empty_heroes(client, api_prefix):
    url = f"{api_prefix}/heroes/"
    response = await client.get(url)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_200_OK
    assert data["results"] == []
    assert data["total"] == 0


async def test_read_heroes(client, api_prefix, db_session):
    # name for seaching
    name_for_seaching = ""
    page = 1
    size = 5
    n = 21
    total_pages = math.ceil(n / size)

    # generate mock data using faker
    for _ in range(n):
        name_for_seaching = fake.name()
        model = HeroCreate(
            name=name_for_seaching,
            age=randint(20, 40),
            secret_name=fake.unique.first_name(),
            hero_publisher_id=randint(1, 2)
        )
        db_hero = Hero.model_validate(model)
        db_session.add(db_hero)

    await db_session.commit()

    # Test Searching
    query_params = {"page": page, "size": size, "search": name_for_seaching}
    url = f"{api_prefix}/heroes/"
    response = await client.get(url, params=query_params)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["results"][0]["name"] == name_for_seaching

    # Sorting ASC
    query_params = {"page": page, "size": size, "sorting": "id:asc"}
    url = f"{api_prefix}/heroes/"
    response = await client.get(url, params=query_params)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["results"] != []
    assert data["total"] == n
    assert data["page"] == page
    assert data["size"] == size
    assert data["pages"] == total_pages
    assert data["results"][0]["id"] == 1

    # Sorting DESC
    query_params["sorting"] = "id:desc"
    url = f"{api_prefix}/heroes/"
    response = await client.get(url, params=query_params)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["results"] != []
    assert data["results"][0]["id"] == 21

    # Sorting Exception
    query_params["sorting"] = "test:desc"
    url = f"{api_prefix}/heroes/"
    response = await client.get(url, params=query_params)
    data = response.json()
    print(data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Sorting formatted incorrectly"
