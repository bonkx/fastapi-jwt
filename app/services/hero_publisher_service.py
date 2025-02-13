from typing import List, Optional

from ..models import HeroPublisher, HeroPublisherCreate, HeroPublisherUpdate
from ..repositories.hero_publisher_repo import HeroPublisherRepository
from .base import BaseService

# Serivce / Use Case


class HeroPublisherService(BaseService):

    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[HeroPublisher]:
        """Retrieve all data from the repository."""
        return await HeroPublisherRepository(self.session).list(search=search, sorting=sorting)

    async def get_by_id(self, id: int) -> HeroPublisher:
        """Retrieve a data by ID."""
        obj = await HeroPublisherRepository(self.session).get_by_id(id)
        return obj

    async def add(self, obj: HeroPublisherCreate) -> HeroPublisher:
        """Add a new data to the repository."""
        return await HeroPublisherRepository(self.session).create(obj)

    async def edit(self, id: int, obj: HeroPublisherUpdate) -> HeroPublisher:
        """Edit data to the repository."""
        return await HeroPublisherRepository(self.session).edit(id=id, obj=obj)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        return await HeroPublisherRepository(self.session).delete(id)
