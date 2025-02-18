# db connection related stuff
import contextlib
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            bind=self._engine, class_=AsyncSession, autocommit=False, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:  # pragma: no cover
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:  # pragma: no cover
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:  # pragma: no cover
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:  # pragma: no cover
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:  # pragma: no cover
            await session.rollback()
            raise
        finally:
            await session.close()


# sessionmanager = DatabaseSessionManager(settings.DATABASE_URL, {"echo": settings.DEBUG})
sessionmanager = DatabaseSessionManager(settings.DATABASE_URL, {"echo": False})


async def get_session():  # pragma: no cover
    async with sessionmanager.session() as session:
        yield session


async def init_db() -> None:  # pragma: no cover
    async with sessionmanager.connect() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# OLD one
# Create Database Engine
# async_engine = AsyncEngine(create_engine(url=settings.DATABASE_URL))

# async def init_db() -> None:
#     async with async_engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

# async def get_session() -> AsyncSession:  # type: ignore
#     Session = sessionmaker(
#         bind=async_engine, class_=AsyncSession, expire_on_commit=False
#     )

#     async with Session() as session:
#         yield session

#         await session.close()
