from typing import List, Optional

from fastapi import HTTPException, status

from ..models.hero import Hero, HeroCreate
from ..repositories.hero_repo import HeroRepository
from ..utils.exceptions import ResponseException
from ..utils.response import ResponseSchema
from .base import BaseService

# Serivce / Use Case


class HeroService(BaseService):
    # async def validate_user_data(self, user_data: UserCreate) -> None:
    #     if not user_data.email or not user_data.password:
    #         raise ValueError("Email and password are required.")

    # async def check_user_exists(self, email: str) -> None:
    #     existing_user = await self.user_repository.get_user_by_email(email)
    #     if existing_user:
    #         raise ValueError("User already exists.")

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
        if obj is None:
            raise ResponseException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hero with ID {id} not found",
                resolution="Try again with another ID"
            )

        return ResponseSchema(result=obj)

    async def add(self, obj: HeroCreate) -> Hero:
        """Add a new data to the repository."""
        # await self.validate_user_data(user_data)
        # await self.check_user_exists(user_data.email)
        return await HeroRepository(self.session).create(obj)

    async def edit(self, id: int, obj: HeroCreate) -> Hero:
        """Edit data to the repository."""
        await self.get_by_id(id)

        return await self.repository.edit(id, obj)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        await self.get_by_id(id)

        return await self.repository.delete(id)
