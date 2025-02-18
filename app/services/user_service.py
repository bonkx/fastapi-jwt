from datetime import datetime, timedelta
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from ..core.config import settings
from ..models import User, UserCreate, UserUpdate
from ..repositories.user_repo import UserRepository
from ..utils.exceptions import UserAlreadyExists, UsernameAlreadyExists
from .base import BaseService


class UserService(BaseService):

    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[User]:
        """Retrieve all data from the repository."""
        return await UserRepository(self.session).list(search=search, sorting=sorting)

    async def get_by_id(self, id: int) -> User:
        """Retrieve a data by ID."""
        obj = await UserRepository(self.session).get_by_id(id)
        return obj

    async def create(self, user_data: UserCreate) -> User:
        """Register a new data to the repository."""

        # validates
        await self.check_user_exists(user_data.email)
        await self.check_username_exists(user_data.username)

        return await UserRepository(self.session).create(user_data)

    async def edit(self, id: int, user_data: UserUpdate) -> User:
        """Edit data to the repository."""
        return await UserRepository(self.session).edit(id=id, obj=user_data)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        return await UserRepository(self.session).delete(id)

    async def check_user_exists(self, email: str) -> None:
        """Check check_user_exists by email."""
        stmt = select(User).where(User.email == email)
        existing_user = await UserRepository(self.session).get_one(stmt)

        if existing_user:
            raise UserAlreadyExists()

    async def check_username_exists(self, username: str) -> None:
        """Check check_user_exists by username."""
        stmt = select(User).where(User.username == username)
        existing_user = await UserRepository(self.session).get_one(stmt)

        if existing_user:
            raise UsernameAlreadyExists()

    async def get_by_email(self, email: str) -> User:
        return await UserRepository(self.session).get_by_email(email)

    async def verify_user(self, user: User) -> User:
        return await UserRepository(self.session).verify_user(user)

    # TODO:
    # forgot password
    # reset password
    # update profile
