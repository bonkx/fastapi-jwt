import math
from datetime import UTC, datetime, timedelta
from random import randint

from bs4 import BeautifulSoup  # type: ignore
from faker import Faker
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.email import fm
from app.core.security import create_url_safe_token, decode_url_safe_token
from app.models import (User, UserCreate, UserLoginModel, UserProfileCreate,
                        UserUpdate)
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

from . import pytest, pytestmark

fake = Faker()


class TestInternalGetUsers:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"admin{self.api_prefix}/users/"

    async def test_get_user_route(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = 1
        user.profile.role = "Admin"

        # update user
        await UserRepository(self.db_session).add_one(user)
        # await self.db_session.refresh(user)

        assert user.is_verified == True
        assert user.profile.status_id == 1
        assert user.profile.role == "Admin"

        # generate token
        token = await AuthService(self.db_session).login_user(UserLoginModel(**self.payload_user_login))

        access_token = token.access_token
        headers = {"Authorization": f"Bearer {access_token}"}

        # get user
        url = f"{self.url}{user.id}"
        response = await self.client.get(url, headers=headers)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_200_OK
        assert "id" in data
        assert data["username"] == "johndoe"

    async def test_get_user_route_no_token(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # get user without token
        url = f"{self.url}{user.id}"
        response = await self.client.get(url)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data["detail"] == "Not authenticated"


class TestInternalDeleteUsers:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"admin{self.api_prefix}/users/"

    async def test_delete_user(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = 1
        user.profile.role = "Admin"

        # update user
        await UserRepository(self.db_session).add_one(user)
        # self.payload_user_register["last_name"] = "Wick"
        # response = await UserRepository(self.db_session).edit(id=user.id, user_data=UserUpdate(**payload_user_register))
        # data = response
        # print(data)

        assert user.is_verified == True
        assert user.profile.status_id == 1
        assert user.profile.role == "Admin"

        # create user for deletion
        fake_email = fake.email()
        fake_user = await UserRepository(self.db_session).create(UserCreate(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            username=fake.user_name(),
            email=fake_email,
            password=fake.password(),
        ))
        assert fake_user.email == fake_email

        # generate token
        token = await AuthService(self.db_session).login_user(UserLoginModel(**self.payload_user_login))

        access_token = token.access_token
        headers = {"Authorization": f"Bearer {access_token}"}

        # delete fake user
        url = f"{self.url}{fake_user.id}"
        # print(url)
        response = await self.client.delete(url, headers=headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""

        # # # Try to get the deleted item
        response = await self.client.get(url, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_no_token(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # delete user
        url = f"{self.url}{user.id}"
        response = await self.client.delete(url)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data["detail"] == "Not authenticated"

    async def test_token_exception(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = 1

        # update user
        await UserRepository(self.db_session).add_one(user)

        assert user.is_verified == True

        headers = {"Authorization": f"Bearer wrong_token"}

        # get user
        url = f"{self.url}{user.id}"
        response = await self.client.get(url, headers=headers)
        data = response.json()
        print(data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert data["detail"] == "Token is invalid Or expired"
