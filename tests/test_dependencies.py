from datetime import datetime

from fastapi import status
from unittest.mock import AsyncMock, MagicMock

from app.core.config import settings
from app.core.security import create_access_token, decode_token
from app.dependencies import GetCurrentUser, get_settings
from app.schemas.user_schema import UserCreateSchema
from app.repositories.user_repo import UserRepository
from app.utils.exceptions import AccountSuspended

from . import pytest, pytestmark


class TestTokenBearer:
    @pytest.fixture(autouse=True)
    def init(self, client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"admin{self.api_prefix}/users/"
        self.auth_url = f"{self.api_prefix}/auth/"
        self.repo = UserRepository(self.db_session)

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        # create user
        user = await self.repo.create(UserCreateSchema(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified, status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = settings.STATUS_USER_ACTIVE
        user.profile.role = "Admin"

        # update user
        await self.repo.add_one(user)
        assert user.is_verified == True
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE
        assert user.profile.role == "Admin"

        self.user = user

    async def test_accesstokenbearer(self):
        # generate refresh token
        refresh_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
            refresh=True,
        )
        access_token = refresh_token
        headers = {"Authorization": f"Bearer {access_token}"}

        # get user
        url = f"{self.url}{self.user.id}"
        response = await self.client.get(url, headers=headers)

        assert response.status_code == 401

    async def test_refreshtokenbearer(self):
        # generate access_token
        access_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        # request refresh token
        url = f"{self.auth_url}refresh-token"

        response = await self.client.post(url, headers=headers)
        data = response.json()

        assert response.status_code == 403
        assert data["detail"] == "Please provide a valid refresh token"

    async def test_rolechecker_accountnotverified(self):
        # update user verified = False
        self.user.is_verified = False

        # update user
        await self.repo.add_one(self.user)
        assert self.user.is_verified == False

        # generate access token
        access_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        # get user
        url = f"{self.url}{self.user.id}"
        response = await self.client.get(url, headers=headers)
        data = response.json()

        assert response.status_code == 403
        assert data["detail"] == "Account Not verified"

    async def test_rolechecker_insufficientpermission(self):
        # update user role = User
        self.user.profile.role = "User"

        # update user
        await self.repo.add_one(self.user)
        assert self.user.profile.role == "User"

        # generate access token
        access_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        # get user
        url = f"{self.url}{self.user.id}"
        response = await self.client.get(url, headers=headers)
        data = response.json()

        assert response.status_code == 403
        assert data["detail"] == "You do not have enough permissions to perform this action"

    async def test_get_current_user(self):
        # generate token
        token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )

        token_details = await decode_token(token)
        # print(token_details)

        # get current user
        get_user = GetCurrentUser()
        response = await get_user(token_details, self.db_session, get_settings())

        assert response.email == self.user.email

    async def test_get_current_user_suspended(self):
        # suspend user
        self.user.profile.status_id = settings.STATUS_USER_SUSPENDED

        # update user
        await self.repo.add_one(self.user)
        assert self.user.profile.status_id == settings.STATUS_USER_SUSPENDED

        # generate token
        token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )

        token_details = await decode_token(token)
        # print(token_details)

        # get current user
        get_user = GetCurrentUser()
        with pytest.raises(AccountSuspended) as exc:
            await get_user(token_details, self.db_session, get_settings())

        assert exc.type == AccountSuspended
