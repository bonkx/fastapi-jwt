from typing import List, Optional

from app.core.config import settings
from app.schemas.user_schema import UserCreateSchema
from app.schemas.auth_schema import LoginSchema
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.exceptions import (AccountNotVerified, AccountSuspended,
                                  InvalidCredentials)

from . import pytest, pytestmark


class TestAuthService:
    @pytest.fixture(autouse=True)
    def init(self, client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.repo = UserRepository(self.db_session)
        self.userSrv = UserService(self.repo)
        self.authSrv = AuthService(self.repo)

    async def test_login_account_not_verified(self):
        # create user
        new_user = await self.userSrv.create(UserCreateSchema(**self.payload_user_register))
        assert new_user.email == "johndoe123@fastapi.com"

        # login
        with pytest.raises(AccountNotVerified) as exc:
            await self.authSrv.login_user(LoginSchema(**self.payload_user_login))

        assert exc.type == AccountNotVerified

    async def test_invalid_credentials(self):
        # create user
        new_user = await self.userSrv.create(UserCreateSchema(**self.payload_user_register))
        assert new_user.email == "johndoe123@fastapi.com"

        # verify user
        user = await self.userSrv.verify_user(new_user)

        assert user.is_verified == 1
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

        # login
        # set wrong password
        self.payload_user_login["password"] = "wrong password"
        with pytest.raises(InvalidCredentials) as exc:
            await self.authSrv.login_user(LoginSchema(**self.payload_user_login))

        assert exc.type == InvalidCredentials

    async def test_login_user_suspended(self):
        # register user
        new_user = await self.userSrv.create(UserCreateSchema(**self.payload_user_register))
        assert "id" in new_user.model_dump()

        # suspend user
        # update user role verified, status
        new_user.is_verified = True
        new_user.profile.status_id = settings.STATUS_USER_SUSPENDED

        # update user
        await self.repo.add_one(new_user)
        assert new_user.is_verified == True
        assert new_user.profile.status_id == settings.STATUS_USER_SUSPENDED

        # test AuthService login user
        with pytest.raises(AccountSuspended) as exc:
            await self.authSrv.login_user(LoginSchema(**self.payload_user_login))

        assert exc.type == AccountSuspended
