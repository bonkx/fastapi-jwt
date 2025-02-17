
from app.repositories.user_repo import UserRepository
from app.utils.exceptions import UserNotFound

from . import pytest, pytestmark


async def test_get_by_email_failed(db_session):
    with pytest.raises(UserNotFound) as exc:
        await UserRepository(db_session).get_by_email(**{"email": "email@test.com"})

    assert exc.type == UserNotFound


async def test_get_by_username_failed(db_session):
    with pytest.raises(UserNotFound) as exc:
        await UserRepository(db_session).get_by_username(**{"username": "johndoe"})

    assert exc.type == UserNotFound
