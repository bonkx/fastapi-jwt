
from abc import ABC, abstractmethod
from typing import List, Optional

from ...models.hero import Hero, HeroCreate


class IHeroRepository(ABC):
    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> List[Hero]:
        """Retrieve all data."""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Hero]:
        """Retrieve a data by its ID."""
        pass

    @abstractmethod
    async def add(self, obj: HeroCreate) -> Hero:
        """Add a new data."""
        pass

    @abstractmethod
    async def edit(self, id: int, obj: HeroCreate) -> Hero:
        """Edit data."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete data."""
        pass
