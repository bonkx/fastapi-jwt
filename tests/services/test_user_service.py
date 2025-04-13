from typing import List, Optional

from app.core.config import settings
from app.models import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.utils.exceptions import (UserAlreadyExists, UsernameAlreadyExists,
                                  UserNotFound)

from . import pytest, pytestmark


async def test_add(db_session, payload_user_register):
    response = await UserService(db_session).create(UserCreate(**payload_user_register))
    data = response
    print(data)

    assert data.first_name == "John"
    assert data.username == "johndoe"
    assert data.email == "johndoe123@fastapi.com"


async def test_add_email_exists(db_session, payload_user_register):
    await UserService(db_session).create(UserCreate(**payload_user_register))

    with pytest.raises(UserAlreadyExists) as exc:
        await UserService(db_session).create(UserCreate(**payload_user_register))

    assert exc.type == UserAlreadyExists


async def test_add_username_exists(db_session, payload_user_register):
    await UserService(db_session).create(UserCreate(**payload_user_register))

    payload_user_register["email"] = "johndoe234@fastapi.com"
    with pytest.raises(UsernameAlreadyExists) as exc:
        await UserService(db_session).create(UserCreate(**payload_user_register))

    assert exc.type == UsernameAlreadyExists


async def test_get(db_session, payload_user_register):
    # MOCK create user using Service
    created = await UserService(db_session).create(UserCreate(**payload_user_register))

    response = await UserService(db_session).get_by_id(id=created.id)
    data = response
    print(data)

    assert data.last_name == "Doe"
    assert data.username == "johndoe"
    assert data.email == "johndoe123@fastapi.com"


async def test_edit(db_session, payload_user_register):
    # MOCK create user using Service
    created = await UserService(db_session).create(UserCreate(**payload_user_register))

    payload_user_register["last_name"] = "Wick"
    response = await UserService(db_session).edit(id=created.id, user_data=UserUpdate(**payload_user_register))
    data = response
    print(data)

    assert data.last_name == "Wick"
    assert data.username == "johndoe"


async def test_delete(db_session, payload_user_register):
    # MOCK create user using Service
    created = await UserService(db_session).create(UserCreate(**payload_user_register))

    await UserService(db_session).delete(id=created.id)

    with pytest.raises(UserNotFound) as exc:
        await UserService(db_session).get_by_id(id=created.id)

    assert exc.type == UserNotFound


async def test_verify_user(db_session, payload_user_register):
    # MOCK create user using Service
    created = await UserService(db_session).create(UserCreate(**payload_user_register))
    assert created.is_verified == 0
    assert created.profile.status_id == settings.STATUS_USER_PENDING

    user = await UserService(db_session).verify_user(created)

    assert user.is_verified == 1
    assert user.profile.status_id == settings.STATUS_USER_ACTIVE
