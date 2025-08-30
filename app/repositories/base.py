import uuid
from typing import Any, Dict, Generic, List, Sequence, Type, TypeVar

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import Executable
from sqlmodel import func, select
from sqlmodel.sql.expression import SelectOfScalar

from ..services.base import SessionMixin


class BaseRepository(SessionMixin):
    """Base repository class responsible for operations over database."""

    async def get_count(self, q: SelectOfScalar) -> int:
        count = await self.session.scalar(
            select(func.count()).select_from(q.subquery())
        )
        # print(count)
        return count if count is not None else 0

    # async def get_count(self, q: SelectOfScalar) -> int:
    #     count_q = q.with_only_columns(func.count()).order_by(None).select_from(*q.froms)
    #     iterator = await self.session.exec(count_q)
    #     for count in iterator:
    #         return count
    #     return 0

    async def get_all(self, statement: Executable) -> List[Any]:
        return await paginate(conn=self.session, query=statement)

    async def get_one(self, statement: Executable) -> Any:
        result = await self.session.exec(statement)
        obj = result.first()

        return obj if obj is not None else None

    async def add_one(self, model: Any) -> None:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return model

    async def add_all(self, models: Sequence[Any]) -> List[Any]:
        self.session.add_all(models)
        await self.session.commit()
        # await self.session.refresh(models)
        return models

    async def delete_one(self, model: Any) -> None:
        await self.session.delete(model)
        await self.session.commit()

        return model
