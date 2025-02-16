import math
from random import randint

from faker import Faker
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.email import fm
from app.models import UserCreate, UserProfileCreate
from app.repositories.hero_publisher_repo import HeroPublisherRepository

from . import pytest, pytestmark


class TestAuthUser:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.url = f"{self.api_prefix}/auth/"

    async def test_user_register(self):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            url = f"{self.url}register"
            response = await self.client.post(url, json=self.payload_user_register)
            data = response.json()
            print(data)

            # {'detail': 'Account Created! Check email to verify your account',
            #  'user': {'id': 1, 'created_at': '2025-02-15T18:39:57.973126', 'updated_at': '2025-02-15T18:39:57.973126', 'first_name': 'John', 'last_name': 'Doe', 'username': 'johndoe', 'email': 'johndoe123@fastapi.com', 'is_verified': False, 'is_superuser': False, 'is_staff': False, 'last_login_at': None, 'last_login_ip': None, 'verified_at': None, 'profile': None}}
            assert response.status_code == status.HTTP_200_OK
            assert data["detail"] == "Account Created! Check email to verify your account"
            assert "id" in data["user"]
            assert data["user"]["username"] == "johndoe"
            assert outbox[0]['To'] == "johndoe123@fastapi.com"

    async def test_user_register_422(self):
        url = f"{self.url}register"
        response = await self.client.post(url, json={})
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_user_register_password_length(self):
        self.payload_user_register["password"] = "123"
        url = f"{self.url}register"
        response = await self.client.post(url, json=self.payload_user_register)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data == {
            "detail": [
                {
                    "type": "string_too_short",
                    "loc": ["body", "password"],
                    "msg": "String should have at least 4 characters",
                    "input": "123",
                    "ctx": {"min_length": 4}
                }
            ]
        }
