import math
from datetime import UTC, datetime, timedelta
from random import randint

from bs4 import BeautifulSoup  # type: ignore
from faker import Faker
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.email import fm
from app.core.security import create_url_safe_token, decode_url_safe_token
from app.models import UserCreate, UserProfileCreate
from app.repositories.user_repo import UserRepository

from . import pytest, pytestmark


class TestInternalUsers:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.url = f"admin{self.api_prefix}/users/"

    async def test_get_user_route(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # get user
        url = f"{self.url}{user.id}"
        response = await self.client.get(url)
        data = response.json()
        # print(data)

        assert response.status_code == status.HTTP_200_OK
        assert "id" in data
        assert data["username"] == "johndoe"

    async def test_delete_user(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # get user
        url = f"{self.url}{user.id}"
        response = await self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""

        # Try to get the deleted item
        response = await self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
