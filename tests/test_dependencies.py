from datetime import datetime

from fastapi import status

from app.core.security import create_access_token
from app.models import UserCreate
from app.repositories.user_repo import UserRepository

from . import pytest, pytestmark


class TestTokenBearer:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"admin{self.api_prefix}/users/"

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
        data = response.json()
        print(data)

        assert response.status_code == 401

    async def test_refreshtokenbearer(self):
        ...
