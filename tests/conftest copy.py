# import asyncio
# from typing import AsyncGenerator, Generator

import asyncio
from contextlib import ExitStack

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.testing.entities import ComparableEntity
from sqlmodel import Session, SQLModel, StaticPool, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.main import app

# DATABASE_URL = 'sqlite+aiosqlite:///test.db'
DATABASE_URL = 'sqlite+aiosqlite:///:memory:'
BASE_URL = 'http://test'

api_version = "v1"
version_prefix = f"/api/{api_version}"


# Create Database Engine
test_async_engine = AsyncEngine(create_engine(
    url=DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool
))


async def ovveride_get_session() -> AsyncSession:  # type: ignore
    TestSession = sessionmaker(
        bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with TestSession() as session:
        yield session

# ovveride Session
app.dependency_overrides[get_session] = ovveride_get_session


# # Create tables in the database
async def init_db() -> None:
    async with test_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
# Run it
asyncio.run(init_db())


@pytest.fixture(autouse=True)
def api_prefix():
    return version_prefix


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
        # await app.router.startup()
        yield client
        # await app.router.shutdown()


# @pytest.fixture(name="session")
# def session_fixture():
#     engine = test_async_engine
#     SQLModel.metadata.create_all(engine)
#     with AsyncSession(engine) as session:
#         yield session
