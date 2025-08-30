from typing import List, Optional

from app.core.config import settings
from app.models import User
from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository
from app.utils.exceptions import (UserAlreadyExists, UsernameAlreadyExists,
                                  UserNotFound)

from . import pytest, pytestmark


class TestUserService:
    @pytest.fixture(autouse=True)
    def init(self, client, api_prefix, db_session, payload_user_register, payload_user_update):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_update = payload_user_update
        self.repo = UserRepository(self.db_session)
        self.srv = UserService(self.repo)

    async def test_add(self):
        response = await self.srv.create(UserCreateSchema(**self.payload_user_register))
        data = response
        print(data)

        assert data.first_name == "John"
        assert data.username == "johndoe"
        assert data.email == "johndoe123@fastapi.com"

    async def test_add_email_exists(self):
        await self.srv.create(UserCreateSchema(**self.payload_user_register))

        with pytest.raises(UserAlreadyExists) as exc:
            await self.srv.create(UserCreateSchema(**self.payload_user_register))

        assert exc.type == UserAlreadyExists

    async def test_add_username_exists(self):
        await self.srv.create(UserCreateSchema(**self.payload_user_register))

        self.payload_user_register["email"] = "johndoe234@fastapi.com"
        with pytest.raises(UsernameAlreadyExists) as exc:
            await self.srv.create(UserCreateSchema(**self.payload_user_register))

        assert exc.type == UsernameAlreadyExists

    async def test_get(self):
        # MOCK create user using Service
        created = await self.srv.create(UserCreateSchema(**self.payload_user_register))

        response = await self.srv.get_by_id(id=created.id)
        data = response
        print(data)

        assert data.last_name == "Doe"
        assert data.username == "johndoe"
        assert data.email == "johndoe123@fastapi.com"

    async def test_edit(self):
        # MOCK create user using Service
        created = await self.srv.create(UserCreateSchema(**self.payload_user_register))

        self.payload_user_update["last_name"] = "Wick"
        response = await self.srv.edit(id=created.id, user_data=UserUpdateSchema(**self.payload_user_update))
        data = response
        print(data)

        assert data.last_name == "Wick"
        assert data.username == "johndoe"

    async def test_delete(self):
        # MOCK create user using Service
        created = await self.srv.create(UserCreateSchema(**self.payload_user_register))

        await self.srv.delete(id=created.id)

        with pytest.raises(UserNotFound) as exc:
            await self.srv.get_by_id(id=created.id)

        assert exc.type == UserNotFound

    async def test_verify_user(self):
        # MOCK create user using Service
        created = await self.srv.create(UserCreateSchema(**self.payload_user_register))
        assert created.is_verified == 0
        assert created.profile.status_id == settings.STATUS_USER_PENDING

        user = await self.srv.verify_user(created)

        assert user.is_verified == 1
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE
