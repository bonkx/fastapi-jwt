from typing import List, Optional

from app.models import UserCreate, UserLoginModel
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.exceptions import AccountNotVerified, InvalidCredentials

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
    assert user.profile.status_id == 1

    # login
    # set wrong password
    payload_user_login["password"] = "wrong password"
    with pytest.raises(InvalidCredentials) as exc:
        await AuthService(db_session).login_user(UserLoginModel(**payload_user_login))

    assert exc.type == InvalidCredentials
