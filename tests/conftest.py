import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import DatabaseSessionManager, get_session
from app.main import app

BASE_URL = 'http://test'
# DATABASE_URL = 'sqlite+aiosqlite:///:memory:'
DATABASE_URL = 'sqlite+aiosqlite:///testdb.sqlite3'


@pytest.fixture(autouse=True)
def sessionmanager():
    return DatabaseSessionManager(DATABASE_URL, {"echo": False})


@pytest.fixture(autouse=True)
def api_prefix():
    return settings.API_PREFIX


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session(sessionmanager):
    """Create a new database session with a rollback at the end of the test."""

    # create table
    async with sessionmanager.connect() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        async with sessionmanager.session() as session:
            yield session
    finally:
        # drop table
        async with sessionmanager.connect() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    await conn.rollback()
    await sessionmanager.close()


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    async def ovveride_get_session() -> AsyncSession:  # type: ignore
        # yield db_session
        try:
            yield db_session
        finally:
            await db_session.close()

    # ovveride Session
    app.dependency_overrides[get_session] = ovveride_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
        yield client


# let test session to know it is running inside event loop
# @pytest.fixture(scope='session')
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(autouse=True)
def payload_hero_publisher():
    return {
        "id": 1,
        "name": "Marvel Comics",
    }


@pytest.fixture(autouse=True)
def payload_hero_publisher_update():
    return {
        "id": 1,
        "name": "Marvel Comics Update",
    }


@pytest.fixture(autouse=True)
def payload_hero():
    return {
        "id": 1,
        "name": "Tony Stark",
        "secret_name": "Iron Man",
        "age": 40,
        "hero_publisher_id": 1,
    }


@pytest.fixture(autouse=True)
def payload_hero_update():
    return {
        "id": 1,
        "name": "Tony Stark Update",
        "secret_name": "Iron Man Update",
        "age": 30,
        "hero_publisher_id": 1,
    }


@pytest.fixture(autouse=True)
def payload_user_register():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "johndoe123@fastapi.com",
        "password": "testpass123",
    }


@pytest.fixture(autouse=True)
def payload_user_update():
    return {
        "first_name": "John",
        "last_name": "Wick",
    }


@pytest.fixture(autouse=True)
def payload_user_login():
    return {
        "email": "johndoe123@fastapi.com",
        "password": "testpass123",
    }
