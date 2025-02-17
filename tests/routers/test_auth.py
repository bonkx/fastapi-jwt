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


class TestVerification:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.url = f"/account/"

    async def test_verify_token(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # get user by username
        get_user = await UserRepository(self.db_session).get_by_username(new_user.username)
        assert get_user.email == new_user.email

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": new_user.email, "exp": expiration_datetime})

        # decode token to get email
        decode_token = await decode_url_safe_token(token)
        assert "email" in decode_token
        assert decode_token["email"] == new_user.email

        # request verify link
        url = f"{self.url}verify/{token}"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Account Verification Successful!"

        # get user again for checking is_verified and status
        user = await UserRepository(self.db_session).get_by_id(new_user.id)
        assert user.is_verified == 1
        assert user.profile.status_id == 1

    async def test_verify_token_failed(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # get user by email
        get_user = await UserRepository(self.db_session).get_by_email(new_user.email)
        assert get_user.email == new_user.email

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": new_user.email, "exp": expiration_datetime})

        # decode token to get email
        decode_token = await decode_url_safe_token(token)
        assert "email" in decode_token
        assert decode_token["email"] == new_user.email

        # request verify link with failed token value
        url = f"{self.url}verify/{token}_token_failed"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Oops... Invalid Token"

        # get user again for checking is_verified and status
        user = await UserRepository(self.db_session).get_by_id(new_user.id)
        assert user.is_verified == 0
        assert user.profile.status_id == 3

    async def test_user_already_verified(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": new_user.email, "exp": expiration_datetime})

        # decode token to get email
        decode_token = await decode_url_safe_token(token)
        assert "email" in decode_token
        assert decode_token["email"] == new_user.email

        # request verify link
        url = f"{self.url}verify/{token}"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.content)

        assert response.status_code == status.HTTP_200_OK

        # request verify link again
        url = f"{self.url}verify/{token}"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.text)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Account already verified"

    # async def test_resend_verification_link(self):
    #     token = await create_url_safe_token({"email": new_user.email, "exp": expiration_datetime})
    #     fm.config.SUPPRESS_SEND = 1
    #     with fm.record_messages() as outbox:
    #         url = f"{self.url}register"
    #         response = await self.client.post(url, json=self.payload_user_register)
    #         data = response.json()
    #         print(data)

    #         # {'detail': 'Account Created! Check email to verify your account',
    #         #  'user': {'id': 1, 'created_at': '2025-02-15T18:39:57.973126', 'updated_at': '2025-02-15T18:39:57.973126', 'first_name': 'John', 'last_name': 'Doe', 'username': 'johndoe', 'email': 'johndoe123@fastapi.com', 'is_verified': False, 'is_superuser': False, 'is_staff': False, 'last_login_at': None, 'last_login_ip': None, 'verified_at': None, 'profile': None}}
    #         assert response.status_code == status.HTTP_200_OK
    #         assert data["detail"] == "Account Created! Check email to verify your account"
    #         assert "id" in data["user"]
    #         assert data["user"]["username"] == "johndoe"
    #         assert outbox[0]['To'] == "johndoe123@fastapi.com"
