
import time
import uuid
from datetime import UTC, datetime, timedelta
from random import randint

from bs4 import BeautifulSoup  # type: ignore
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.config import settings
from app.core.email import fm
from app.core.redis import add_jti_to_blocklist
from app.core.security import (create_url_safe_token, decode_token,
                               decode_url_safe_token)
from app.models import UserCreate
from app.repositories.user_repo import UserRepository

from . import pytest, pytestmark


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
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

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

        # get user again for checking is_verified and status pending
        user = await UserRepository(self.db_session).get_by_id(self.user.id)
        assert user.is_verified == 0
        assert user.profile.status_id == settings.STATUS_USER_PENDING

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

    async def test_verification_user_suspended(self):
        # update user to status suspended
        self.user.profile.status_id = settings.STATUS_USER_SUSPENDED

        # update user
        await UserRepository(self.db_session).add_one(self.user)
        assert self.user.profile.status_id == settings.STATUS_USER_SUSPENDED

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
        # print('content', response.text)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Account has been suspended. Try registering a new one"

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


class TestResetPassword:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"/account/"
        self.auth_url = f"{self.api_prefix}/auth/"

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        # register user
        new_user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # update user verified, status
        new_user.is_verified = True
        new_user.verified_at = datetime.now()
        new_user.profile.status_id = settings.STATUS_USER_ACTIVE

        # update user
        await UserRepository(self.db_session).add_one(new_user)
        assert new_user.is_verified == True
        assert new_user.profile.status_id == settings.STATUS_USER_ACTIVE

        self.user = new_user

    async def test_get_password_reset_confirm(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "resend_verification_link"
        })

        # request password-reset-confirm
        url = f"{self.url}password-reset-confirm/{token}"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Please change your password"

    async def test_get_password_reset_confirm_wrong_action(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "wrong_action"
        })

        # test token action wrong value
        url = f"{self.url}password-reset-confirm/{token}"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Oops... Invalid Token"

    async def test_get_password_reset_confirm_token_in_blocklist(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "resend_verification_link"
        })

        # decode token
        decode_token = await decode_url_safe_token(token)
        # add token to blocklist
        await add_jti_to_blocklist(decode_token["jti"])

        # test token token_in_blocklist
        url = f"{self.url}password-reset-confirm/{token}"
        response = await self.client.get(url)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Token is invalid Or expired"

    async def test_post_password_reset_confirm(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "resend_verification_link"
        })

        # request password-reset-confirm
        url = f"{self.url}password-reset-confirm/{token}"
        payload = {
            "new_password": "new_password",
            "confirm_new_password": "new_password",
        }
        response = await self.client.post(url, data=payload)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Password reset Successfully"

        # test login with old password
        url = f"{self.auth_url}login"
        response = await self.client.post(url, json=self.payload_user_login)
        data = response.json()
        print(data)

        assert response.status_code == 400
        assert data["detail"] == "Invalid Email Or Password"

    async def test_post_password_reset_confirm_wrong_action(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "wrong_action"
        })

        # request password-reset-confirm
        url = f"{self.url}password-reset-confirm/{token}"
        payload = {
            "new_password": "new_password",
            "confirm_new_password": "new_password",
        }
        response = await self.client.post(url, data=payload)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Oops... Invalid Token"

    async def test_post_password_reset_confirm_token_in_blocklist(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "resend_verification_link"
        })

        # decode token
        decode_token = await decode_url_safe_token(token)
        # add token to blocklist
        await add_jti_to_blocklist(decode_token["jti"])

        # test token token_in_blocklist
        url = f"{self.url}password-reset-confirm/{token}"
        payload = {
            "new_password": "new_password",
            "confirm_new_password": "new_password",
        }
        response = await self.client.post(url, data=payload)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Token is invalid Or expired"

    async def test_post_password_reset_confirm_password_failed(self):
        email = self.payload_user_register["email"]

        # generate token
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "jti": str(uuid.uuid4()),
            "action": "resend_verification_link"
        })

        # request password-reset-confirm
        url = f"{self.url}password-reset-confirm/{token}"
        payload = {
            "new_password": "password",
            "confirm_new_password": "did_not_match_password",
        }
        response = await self.client.post(url, data=payload)
        # print(response)
        # print('content', response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.select_one('h1.__msg__')

        assert response.status_code == status.HTTP_200_OK
        assert h1.text == "Passwords did not match or check length of your password again."
