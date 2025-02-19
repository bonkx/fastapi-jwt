import math
import time
from datetime import UTC, datetime, timedelta
from random import randint

from bs4 import BeautifulSoup  # type: ignore
from faker import Faker
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.email import fm
from app.core.security import (create_access_token, create_url_safe_token,
                               decode_token, decode_url_safe_token)
from app.models import UserCreate, UserProfileCreate
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.exceptions import InvalidToken

from . import pytest, pytestmark


class TestAuthUser:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"{self.api_prefix}/auth/"

    async def test_user_register(self):
        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            url = f"{self.url}register"
            response = await self.client.post(url, json=self.payload_user_register)
            data = response.json()
            print(data)

            assert response.status_code == status.HTTP_200_OK
            assert data["detail"] == "Account Created! Check email to verify your account"
            assert "id" in data["user"]
            assert data["user"]["username"] == "johndoe"
            assert len(outbox) == 1  # mock email sent
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

    async def test_login_user(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # verify user
        user = await UserService(self.db_session).verify_user(new_user)
        assert user.is_verified == 1
        assert user.profile.status_id == 1

        url = f"{self.url}login"
        response = await self.client.post(url, json=self.payload_user_login)
        data = response.json()
        # print(data)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == self.payload_user_login["email"]

    async def test_login_user_failed(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        url = f"{self.url}login"

        # test user not verified yet
        response = await self.client.post(url, json=self.payload_user_login)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data["detail"] == "Account Not verified"

        # verify user
        user = await UserService(self.db_session).verify_user(new_user)
        assert user.is_verified == 1
        assert user.profile.status_id == 1

        # test wrong email (404)
        payload = {
            "email": "123@fastapi.com",
            "password": self.payload_user_login["password"]
        }
        response = await self.client.post(url, json=payload)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "User not found"

        # test wrong password (400)
        payload = {
            "email": self.payload_user_login["email"],
            "password": "wrong_password",
        }
        response = await self.client.post(url, json=payload)
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["detail"] == "Invalid Email Or Password"


class TestVerification:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.url = f"/account/"

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        self.user = new_user

    async def test_verify_token(self):
        # get user by username
        get_user = await UserRepository(self.db_session).get_by_username(self.user.username)
        assert get_user.email == self.user.email

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": self.user.email, "exp": expiration_datetime})

        # decode token to get email
        decode_token = await decode_url_safe_token(token)
        assert "email" in decode_token
        assert decode_token["email"] == self.user.email

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
        user = await UserRepository(self.db_session).get_by_id(self.user.id)
        assert user.is_verified == 1
        assert user.profile.status_id == 1

    async def test_verify_token_failed(self):
        # get user by email
        get_user = await UserRepository(self.db_session).get_by_email(self.user.email)
        assert get_user.email == self.user.email

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": self.user.email, "exp": expiration_datetime})

        # decode token to get email
        decode_token = await decode_url_safe_token(token)
        assert "email" in decode_token
        assert decode_token["email"] == self.user.email

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
        user = await UserRepository(self.db_session).get_by_id(self.user.id)
        assert user.is_verified == 0
        assert user.profile.status_id == 3

    async def test_user_already_verified(self):
        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": self.user.email, "exp": expiration_datetime})

        # decode token to get email
        decode_token = await decode_url_safe_token(token)
        assert "email" in decode_token
        assert decode_token["email"] == self.user.email

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

    async def test_resend_verification_link(self):
        token_resend = await create_url_safe_token({"email": self.user.email, "action": "resend_verification_link"})

        # decode token to get email
        decode_token = await decode_url_safe_token(token_resend)
        assert "email" in decode_token
        assert decode_token["email"] == self.user.email

        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            url = f"{self.url}resend-verification/{token_resend}"
            response = await self.client.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')
            h1 = soup.select_one('h1.__msg__')

            assert response.status_code == status.HTTP_200_OK
            assert h1.text == "New verification email has been successfully sent"
            assert len(outbox) == 1  # mock email sent
            assert outbox[0]['To'] == "johndoe123@fastapi.com"

    async def test_resend_verification_link_failed(self):
        token_resend = await create_url_safe_token({"email": self.user.email, "action": "resend_verification_link"})

        # decode token to get email
        decode_token = await decode_url_safe_token(token_resend)
        assert "email" in decode_token
        assert decode_token["email"] == self.user.email

        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            url = f"{self.url}resend-verification/{token_resend}_failed_token"
            response = await self.client.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')
            h1 = soup.select_one('h1.__msg__')

            assert response.status_code == status.HTTP_200_OK
            assert h1.text == "Oops... Invalid Token"
            assert len(outbox) == 0  # mock email not sent


class TestTokenAuth:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.url = f"{self.api_prefix}/auth/"

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified, status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = 1
        user.profile.role = "Admin"

        # update user
        await UserRepository(self.db_session).add_one(user)
        assert user.is_verified == True
        assert user.profile.status_id == 1
        assert user.profile.role == "Admin"

        self.user = user

    async def test_get_refresh_token(self):
        # generate refresh_token
        refresh_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
            refresh=True,
        )
        headers = {"Authorization": f"Bearer {refresh_token}"}

        # reqeust refresh token
        url = f"{self.url}refresh-token"
        response = await self.client.post(url, headers=headers)
        data = response.json()
        print(data)

        assert response.status_code == 200
        assert "access_token" in data

    async def test_get_new_access_token_failed(self):
        # generate refresh_token
        refresh_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
            refresh=True,
            expiry=timedelta(seconds=1)
        )

        token_details = await decode_token(refresh_token)
        # print(token_details)

        # add time gap
        time.sleep(2)

        # get_new_access_token
        with pytest.raises(InvalidToken) as exc:
            await AuthService(self.db_session).get_new_access_token(token_details)

        assert exc.type == InvalidToken
