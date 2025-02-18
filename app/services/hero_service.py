from typing import List, Optional

from fastapi import HTTPException, status

from ..models import Hero, HeroCreate, HeroUpdate
from ..repositories.hero_repo import HeroRepository
from ..utils.exceptions import ResponseException
from .base import BaseService

# Serivce / Use Case


class HeroService(BaseService):

    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[Hero]:
        """Retrieve all data from the repository."""
        return await HeroRepository(self.session).list(search=search, sorting=sorting)

    async def get_by_id(self, id: int) -> Hero:
        """Retrieve a data by ID."""
        obj = await HeroRepository(self.session).get_by_id(id)
        return obj

    async def create(self, obj: HeroCreate) -> Hero:
        """Add a new data to the repository."""
        return await HeroRepository(self.session).create(obj)

    async def edit(self, id: int, obj: HeroUpdate) -> Hero:
        """Edit data to the repository."""
        return await HeroRepository(self.session).edit(id=id, obj=obj)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        return await HeroRepository(self.session).delete(id)
