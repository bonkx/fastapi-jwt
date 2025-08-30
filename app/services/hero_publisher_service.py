from typing import List, Optional

from ..models import HeroPublisher, HeroPublisherCreateSchema, HeroPublisherUpdateSchema
from ..repositories.hero_publisher_repo import HeroPublisherRepository
from .base import BaseService

# Serivce / Use Case


class HeroPublisherService(BaseService):
    def __init__(self, repo: HeroPublisherRepository):
        self.repo = repo

    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[HeroPublisher]:
        """Retrieve all data from the repository."""
        return await self.repo.list(search=search, sorting=sorting)

    async def get_by_id(self, id: int) -> HeroPublisher:
        """Retrieve a data by ID."""
        obj = await self.repo.get_by_id(id)
        return obj

    async def create(self, obj: HeroPublisherCreateSchema) -> HeroPublisher:
        """Add a new data to the repository."""
        return await self.repo.create(obj)

    async def edit(self, id: int, obj: HeroPublisherUpdateSchema) -> HeroPublisher:
        """Edit data to the repository."""
        return await self.repo.edit(id=id, obj=obj)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        return await self.repo.delete(id)
