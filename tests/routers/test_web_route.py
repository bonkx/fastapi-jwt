
import math
import time
from datetime import UTC, datetime, timedelta
from random import randint

from bs4 import BeautifulSoup  # type: ignore
from fastapi import status
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from app.core.email import fm
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
