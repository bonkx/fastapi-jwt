
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, select

from ..models.hero import Hero, HeroCreate, HeroUpdate
from .base import BaseRepository


class HeroRepository(BaseRepository):
    async def list(self, limit: int, offset: int) -> List[Hero]:
        """Retrieve all data."""
        stmt = select(Hero)
        stmt = stmt.offset(offset).limit(limit)

        return await self.get_all(stmt)

    async def get_by_id(self, id: int) -> Optional[Hero]:
        """Retrieve a data by its ID."""
        stmt = select(Hero).where(Hero.id == id)
        res = await self.get_one(stmt)
        if not res:
            return None

        return res

    async def create(self, obj: HeroCreate) -> Hero:
        """Add a new data."""
        # validate basemodel
        data_dict = obj.model_dump()
        new_model = Hero(**data_dict)

        res = await self.add_one(new_model)
        return res

    async def edit(self, id: int, obj: HeroUpdate) -> Hero:
        """Edit data."""
        pass

    async def delete(self, id: int) -> None:
        """Delete data."""
        pass
