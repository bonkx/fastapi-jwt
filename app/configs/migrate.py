import asyncio

from sqlmodel import SQLModel, create_engine

from .env import settings


async def migrate_tables() -> None:
    print("Starting to migrate")

    # Create Database Engine
    connect_args = {"check_same_thread": False}
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    print("Done migrating")


if __name__ == "__main__":
    asyncio.run(migrate_tables())
