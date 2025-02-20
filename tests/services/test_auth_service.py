from typing import List, Optional

from app.core.config import settings
from app.models import UserCreate, UserLoginModel
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.exceptions import (AccountNotVerified, AccountSuspended,
                                  InvalidCredentials)

from . import pytest, pytestmark


async def test_login_account_not_verified(db_session, payload_user_register, payload_user_login):
    # create user
    new_user = await UserService(db_session).create(UserCreate(**payload_user_register))
    assert new_user.email == "johndoe123@fastapi.com"

    # login
    with pytest.raises(AccountNotVerified) as exc:
        await AuthService(db_session).login_user(UserLoginModel(**payload_user_login))

    assert exc.type == AccountNotVerified


async def test_invalid_credentials(db_session, payload_user_register, payload_user_login):
    # create user
    new_user = await UserService(db_session).create(UserCreate(**payload_user_register))
    assert new_user.email == "johndoe123@fastapi.com"

    # verify user
    user = await UserService(db_session).verify_user(new_user)

    assert user.is_verified == 1
    assert user.profile.status_id == settings.STATUS_USER_ACTIVE

    # login
    # set wrong password
    payload_user_login["password"] = "wrong password"
    with pytest.raises(InvalidCredentials) as exc:
        await AuthService(db_session).login_user(UserLoginModel(**payload_user_login))

    assert exc.type == InvalidCredentials


async def test_login_user_suspended(db_session, payload_user_register, payload_user_login):
    # register user
    new_user = await UserService(db_session).create(UserCreate(**payload_user_register))
    assert "id" in new_user.model_dump()

    # suspend user
    # update user role verified, status
    new_user.is_verified = True
    new_user.profile.status_id = settings.STATUS_USER_SUSPENDED

    # update user
    await UserRepository(db_session).add_one(new_user)
    assert new_user.is_verified == True
    assert new_user.profile.status_id == settings.STATUS_USER_SUSPENDED

    # test AuthService login user
    with pytest.raises(AccountSuspended) as exc:
        await AuthService(db_session).login_user(UserLoginModel(**payload_user_login))

    assert exc.type == AccountSuspended
