
from typing import List, Optional

from fastapi import status
from sqlalchemy.sql import text
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from ..models import HeroPublisher, HeroPublisherCreate, HeroPublisherUpdate
from ..utils.exceptions import ResponseException
from ..utils.validation import formatSorting
from .base import BaseRepository


class HeroPublisherRepository(BaseRepository):
    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None
    ) -> List[HeroPublisher]:
        """Retrieve all data."""
        stmt = select(HeroPublisher)

        if search:
            stmt = stmt.where(
                col(HeroPublisher.name).icontains(search),
            )

        if sorting:
            xSort = formatSorting(HeroPublisher, sorting)
            stmt = stmt.order_by(text(xSort))

        return await self.get_all(stmt)

    async def get_by_id(self, id: int) -> Optional[HeroPublisher]:
        """Retrieve a data by its ID."""
        stmt = select(HeroPublisher).where(HeroPublisher.id == id)
        res = await self.get_one(stmt)

        if res is None:
            raise ResponseException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data with ID {id} not found",
                resolution="Try again with another ID"
            )

        return res

    async def create(self, obj: HeroPublisherCreate) -> HeroPublisher:
        """Add a new data."""
        # validate basemodel
        db_dict = HeroPublisher.model_validate(obj)

        res = await self.add_one(db_dict)
        return res

    async def edit(self, id: int, obj: HeroPublisherUpdate) -> HeroPublisher:
        """Edit data."""
        # get data
        data_db = await self.get_by_id(id)

        # validate payload
        dump_data = obj.model_dump(exclude_unset=True)
        # update payload to data
        data_db.sqlmodel_update(dump_data)

        # process save data
        res = await self.add_one(data_db)
        return res

    async def delete(self, id: int) -> None:
        """Delete data."""
        hero_db = await self.get_by_id(id)
        return await self.delete_one(hero_db)
