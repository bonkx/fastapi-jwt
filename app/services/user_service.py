from datetime import datetime, timedelta
from typing import List, Optional

from ..core.config import settings
from ..models import User
from ..repositories.user_repo import UserRepository
from ..schemas.auth_schema import PasswordResetConfirmSchema
from ..schemas.user_schema import UserCreateSchema, UserSchema, UserUpdateSchema

from .base import BaseService


class UserService(BaseService):
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[User]:
        """Retrieve all data from the repository."""
        return await self.repo.list(search=search, sorting=sorting)

    async def get_by_id(self, id: int) -> User:
        """Retrieve a data by ID."""
        obj = await self.repo.get_by_id(id)
        return obj

    async def create(self, user_data: UserCreateSchema) -> User:
        """Register a new data to the repository."""

        # validates
        await self.repo.check_user_exists(user_data.email)
        await self.repo.check_username_exists(user_data.username)

        return await self.repo.create(user_data)

    async def edit(self, id: int, user_data: UserUpdateSchema) -> User:
        """Edit data to the repository."""
        return await self.repo.edit(id=id, obj=user_data)

    async def delete(self, id: int) -> None:
        """Delete data to the repository."""
        return await self.repo.delete(id)

    async def get_by_email(self, email: str) -> User:
        return await self.repo.get_by_email(email)

    async def verify_user(self, user: User) -> User:
        return await self.repo.verify_user(user)

    async def reset_password(self, user: User, payload: PasswordResetConfirmSchema) -> User:
        return await self.repo.reset_password(user, payload)

    async def update_profile(self, user: User, payload: UserUpdateSchema) -> User:
        # validate payload
        UserUpdateSchema.model_validate(payload)

        return await self.repo.update_profile(user, payload)

    async def update_photo_profile(self, user: User, file_path: str) -> User:
        return await self.repo.update_photo_profile(user, file_path)

    # TODO:
    # reset password
