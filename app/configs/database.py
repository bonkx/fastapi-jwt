# db connection related stuff
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings

# Create Database Engine
async_engine = AsyncEngine(create_engine(url=settings.DATABASE_URL))


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:  # type: ignore
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session


# def get_session():
#     with Session(engine) as session:
#         yield session


# SessionDep = Annotated[Session, Depends(get_session)]
