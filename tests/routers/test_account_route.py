from datetime import datetime

from app.core.config import settings
from app.core.security import create_access_token
from app.models import UserCreate
from app.repositories.user_repo import UserRepository

from . import pytest, pytestmark


class TestAccountUser:
    @pytest.fixture(autouse=True)
    def init(self,  client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.url = f"{self.api_prefix}/account/"

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreate(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified, status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = settings.STATUS_USER_ACTIVE

        # update user
        await UserRepository(self.db_session).add_one(user)
        assert user.is_verified == True
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

        self.user = user

    async def test_get_profile(self):
        # generate access_token
        access_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        # request refresh token
        url = f"{self.url}me"
        response = await self.client.get(url, headers=headers)
        data = response.json()
        print(data)

        assert response.status_code == 200
        assert "id" in data
        assert data["email"] == self.user.email

    async def test_get_profile_accountsuspended(self):
        # update user suspended
        self.user.profile.status_id = settings.STATUS_USER_SUSPENDED

        # update user
        await UserRepository(self.db_session).add_one(self.user)
        assert self.user.profile.status_id == settings.STATUS_USER_SUSPENDED

        # generate access_token
        access_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        # request refresh token
        url = f"{self.url}me"
        response = await self.client.get(url, headers=headers)
        data = response.json()
        print(data)

        assert response.status_code == 401
        assert data["detail"] == "Account has been Suspended"
