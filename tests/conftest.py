import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, StaticPool, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.main import app

BASE_URL = 'http://test'
DATABASE_URL = 'sqlite+aiosqlite:///:memory:'
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

TestSession = sessionmaker(
    bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True)
def api_prefix():
    return version_prefix


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session():
    """Create a new database session with a rollback at the end of the test."""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSession() as session:
        yield session
        await session.close()

    # async with test_async_engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all)

    await conn.rollback()
    await conn.close()


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    async def ovveride_get_session() -> AsyncSession:  # type: ignore
        yield db_session
        # try:
        #     yield db_session
        # finally:
        #     await db_session.close()

    # ovveride Session
    app.dependency_overrides[get_session] = ovveride_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
        yield client
