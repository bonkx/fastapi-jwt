from typing import List, Optional

from fastapi import HTTPException, status

from ..models import Hero, HeroCreateSchema, HeroUpdateSchema
from ..repositories.hero_repo import HeroRepository
from ..utils.exceptions import ResponseException

from .base import BaseService

# Serivce / Use Case


class HeroService(BaseService):
    def __init__(self, repo: HeroRepository):
        self.repo = repo

    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[Hero]:
        """Retrieve all data from the repository."""
        return await self.repo.list(search=search, sorting=sorting)

    async def get_by_id(self, id: int) -> Hero:
        """Retrieve a data by ID."""
        obj = await self.repo.get_by_id(id)
        return obj

    async def create(self, obj: HeroCreateSchema) -> Hero:
        """Add a new data to the repository."""
        return await self.repo.create(obj)

    async def edit(self, id: int, obj: HeroUpdateSchema) -> Hero:
        """Edit data to the repository."""
        return await self.repo.edit(id=id, obj=obj)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        return await self.repo.delete(id)
