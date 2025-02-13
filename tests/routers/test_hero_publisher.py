import math
from random import randint
from unittest import TestCase

from faker import Faker
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.models import HeroPublisher, HeroPublisherCreate
from app.repositories import HeroPublisherRepository

from . import pytest, pytestmark

fake = Faker()


class TestCreateHeroPublisher:

    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.url = f"{self.api_prefix}/hero-publishers/"

    async def test_create_data(self):
        url = self.url
        response = await self.client.post(url, json=self.payload_hero_publisher)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_201_CREATED
        assert data["name"] == "Marvel Comics"
        assert "id" in data

    async def test_create_data_422_exception(self):
        url = self.url
        response = await self.client.post(url, json={})
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_data_validation(self):
        payload = self.payload_hero_publisher

        # TEST name exception
        # set name invalid value
        payload["name"] = 1

        url = self.url
        response = await self.client.post(url, json=payload)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data == {
            "detail": [
                {
                    "type": "string_type",
                    "loc": ["body", "name"],
                    "msg": "Input should be a valid string",
                    "input": 1
                }
            ]
        }


class TestGetHeroPublisher:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.url = f"{self.api_prefix}/hero-publishers/"

    async def test_get_data(self):
        # MOCK create hero using Repo
        payload = self.payload_hero_publisher
        created = await HeroPublisherRepository(self.db_session).create(payload)

        id = created.id

        url = f"{self.url}{id}"
        response = await self.client.get(url)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_200_OK
        assert data["name"] == "Marvel Comics"
        assert data["id"] == id

    async def test_get_data_not_found(self):
        id = 2

        url = f"{self.url}{id}"
        response = await self.client.get(url)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == f"Data with ID {id} not found"

    async def test_get_data_count(self):
        # change value for sequence insert
        payload1 = {"name": "Marvel Comics"}
        payload2 = {"name": "DC Comics"}

        # MOCK create multi data using Repo
        response = await HeroPublisherRepository(self.db_session).add_all(
            [
                HeroPublisher(**payload1),
                HeroPublisher(**payload2),
            ]
        )
        assert len(response) == 2

        # get count data
        response = await HeroPublisherRepository(self.db_session).get_count(select(HeroPublisher))

        assert response == 2


class TestUpdateHeroPublisher:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.url = f"{self.api_prefix}/hero-publishers/"

    async def test_update_hero(self):
        # MOCK create data using Repo
        created = await HeroPublisherRepository(self.db_session).create(self.payload_hero_publisher)

        id = created.id

        url = f"{self.url}{id}"
        response = await self.client.put(url, json=self.payload_hero_publisher_update)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_200_OK
        assert data["name"] == "Marvel Comics Update"
        assert data["id"] == id

    async def test_update_data_wrong_payload(self):
        id = self.payload_hero_publisher_update['id']

        self.payload_hero_publisher_update["name"] = (
            True  # name should be a string not a boolean
        )

        url = f"{self.url}{id}"
        response = await self.client.put(url, json=self.payload_hero_publisher_update)
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

    async def test_update_data_not_found(self):
        id = 2
        url = f"{self.url}{id}"

        response = await self.client.put(url, json=self.payload_hero_publisher_update)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == f"Data with ID {id} not found"


class TestDeleteHeroPublisher:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.url = f"{self.api_prefix}/hero-publishers/"

    async def test_delete_hero(self):
        # MOCK create data using Repo
        created = await HeroPublisherRepository(self.db_session).create(self.payload_hero_publisher)

        id = created.id

        url = f"{self.url}{id}"
        response = await self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""

        # Try to get the deleted item
        response = await self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListHeroPublisher:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_hero_publisher, payload_hero_publisher_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_hero_publisher = payload_hero_publisher
        self.payload_hero_publisher_update = payload_hero_publisher_update
        self.url = f"{self.api_prefix}/hero-publishers/"

    async def test_read_empty_list(self):
        url = self.url
        response = await self.client.get(url)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_200_OK
        assert data["results"] == []
        assert data["total"] == 0

    async def test_read_list(self):
        # value for seaching
        value_for_seaching = ""
        page = 1
        size = 5
        n = 21
        total_pages = math.ceil(n / size)

        data_list = []
        # generate mock data using faker
        for _ in range(n):
            value_for_seaching = fake.name()
            model = HeroPublisherCreate(
                name=value_for_seaching,
            )
            db_model = HeroPublisher.model_validate(model)
            # self.db_session.add(db_hero)
            data_list.append(db_model)

        await HeroPublisherRepository(self.db_session).add_all(data_list)

        url = self.url

        # Test List
        query_params = {"page": page, "size": size}
        response = await self.client.get(url, params=query_params)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["results"] != []
        assert data["total"] == n
        assert data["page"] == page
        assert data["size"] == size
        assert data["pages"] == total_pages

        # Test Searching
        query_params = {"page": page, "size": size, "search": value_for_seaching}
        response = await self.client.get(url, params=query_params)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["results"][0]["name"] == value_for_seaching

        # Test Sorting ASC
        query_params = {"page": page, "size": size, "sorting": "id:asc"}
        response = await self.client.get(url, params=query_params)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["results"] != []
        assert data["results"][0]["id"] == 1

        # Sorting DESC
        query_params["sorting"] = "id:desc"
        response = await self.client.get(url, params=query_params)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["results"] != []
        assert data["results"][0]["id"] == 21

        # Test Sorting Exception
        query_params["sorting"] = "city:desc"
        response = await self.client.get(url, params=query_params)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["detail"] == "Sorting formatted incorrectly"
