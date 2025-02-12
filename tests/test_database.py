from sqlmodel import SQLModel

from app.core.database import DatabaseSessionManager
from app.services.hero_service import HeroService

from . import pytest, pytestmark

# async def test_session_exception(db_session, payload_hero):
#     sessionmanager = DatabaseSessionManager(None).__init__
#     async with sessionmanager.connect() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

#     # async with sessionmanager.session() as session:
#     #     response = await HeroService(session).add(payload_hero)
#     #     data = response
#     #     print(data)
#     # raise Exception()
