import time
from datetime import UTC, datetime, timedelta

from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.config import settings
from app.core.email import fm
from app.core.security import create_access_token, decode_token
from app.models import UserCreate
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
        self.account_url = f"{self.api_prefix}/account/"

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
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

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
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

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

    async def test_logout_user(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # verify user
        user = await UserService(self.db_session).verify_user(new_user)
        assert user.is_verified == 1
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

        # generate access_token
        access_token = await create_access_token(
            user_data={"email": new_user.email, "user_id": str(new_user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        # post logout
        url = f"{self.url}logout"
        response = await self.client.post(url, headers=headers)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["detail"] == "Logged Out Successfully"

        # get profile
        url = f"{self.account_url}me"
        response = await self.client.get(url, headers=headers)
        data = response.json()

        assert response.status_code == 401
        assert data["detail"] == "Token is invalid Or expired"


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
        user.profile.status_id = settings.STATUS_USER_ACTIVE
        user.profile.role = "Admin"

        # update user
        await UserRepository(self.db_session).add_one(user)
        assert user.is_verified == True
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE
        assert user.profile.role == "Admin"

        self.user = user

    async def test_get_refresh_token(self):
        # generate refresh_token
        refresh_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
            refresh=True,
        )
        headers = {"Authorization": f"Bearer {refresh_token}"}

        # request refresh token
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


class TestResetPassword:
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

        # update verified, status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = settings.STATUS_USER_ACTIVE

        # update user
        await UserRepository(self.db_session).add_one(user)
        assert user.is_verified == True
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

        self.user = user

    async def test_password_reset_request(self):
        email = self.payload_user_register["email"]

        fm.config.SUPPRESS_SEND = 1
        with fm.record_messages() as outbox:
            # request password-reset-request
            url = f"{self.url}password-reset-request"
            response = await self.client.post(url, json={"email": email})
            data = response.json()
            print(data)

            assert response.status_code == 200
            assert data["detail"] == "Please check your email for instructions to reset your password"

            assert len(outbox) == 1  # mock email sent
            assert outbox[0]['To'] == email

    async def test_password_reset_request_failed(self):
        # test validate email
        url = f"{self.url}password-reset-request"
        response = await self.client.post(url, json={"email": "email"})
        data = response.json()

        assert response.status_code == 422
        assert data["detail"][0]["loc"][1] == "email"
        assert data["detail"][0]["msg"] == "value is not a valid email address: An email address must have an @-sign."

        # request password-reset-request
        url = f"{self.url}password-reset-request"
        response = await self.client.post(url, json={"email": "email@email.com"})
        data = response.json()
        print(data)

        assert response.status_code == 404
        assert data["detail"] == "User not found"
