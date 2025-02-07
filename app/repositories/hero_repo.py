
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, select

from ..models.hero import Hero, HeroCreate, HeroUpdate
from .base import BaseRepository
from .interfaces.hero_ifc import IHeroRepository


class HeroRepository(BaseRepository):
    async def list(self, limit: int, offset: int) -> List[Hero]:
        """Retrieve all data."""
        schemas: List[Hero] = list()

        stmt = select(Hero)
        stmt = stmt.offset(offset).limit(limit)

        for model in self.get_all(stmt):
            schemas += [Hero(**model.model_dump())]

        return schemas

    async def get_by_id(self, id: int) -> Optional[Hero]:
        """Retrieve a data by its ID."""
        stmt = select(Hero).where(Hero.id == id)
        model = self.get_one(stmt)
        if not model:
            return None

        return Hero(**model.model_dump())

    async def create(self, obj: HeroCreate) -> Hero:
        """Add a new data."""
        # validate basemodel
        model = Hero.model_validate(obj)

        model = self.add_one(model)
        return Hero(**model.model_dump())

    async def edit(self, id: int, obj: HeroUpdate) -> Hero:
        """Edit data."""
        pass

    async def delete(self, id: int) -> None:
        """Delete data."""
        pass
