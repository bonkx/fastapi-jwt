
from typing import List, Optional

from fastapi import status
from sqlalchemy.sql import text
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from ..models.hero import Hero, HeroCreate, HeroUpdate
from ..utils.exceptions import ResponseException
from ..utils.validation import formatSorting
from .base import BaseRepository


class HeroRepository(BaseRepository):
    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None
    ) -> List[Hero]:
        """Retrieve all data."""
        stmt = select(Hero)

        if search:
            stmt = stmt.where(
                or_(
                    col(Hero.name).icontains(search),
                    col(Hero.secret_name).icontains(search),
                )
            )

        if sorting:
            xSort = formatSorting(sorting)
            stmt = stmt.order_by(text(xSort))

        return await self.get_all(stmt)

    async def get_by_id(self, id: int) -> Optional[Hero]:
        """Retrieve a data by its ID."""
        stmt = select(Hero).where(Hero.id == id)
        res = await self.get_one(stmt)

        if res is None:
            raise ResponseException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hero with ID {id} not found",
                resolution="Try again with another ID"
            )

        return res

    async def create(self, obj: HeroCreate) -> Hero:
        """Add a new data."""
        # validate basemodel
        db_hero = Hero.model_validate(obj)

        res = await self.add_one(db_hero)
        return res

    async def edit(self, id: int, obj: HeroUpdate) -> Hero:
        """Edit data."""
        hero_db = await self.get_by_id(id)
        hero_data = obj.model_dump(exclude_unset=True)
        hero_db.sqlmodel_update(hero_data)

        res = await self.add_one(hero_db)
        return res

    async def delete(self, id: int) -> None:
        """Delete data."""
        hero_db = await self.get_by_id(id)
        return await self.delete_one(hero_db)
