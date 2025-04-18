
from datetime import datetime
from typing import List, Optional

from fastapi import status
from sqlalchemy.sql import text
from sqlmodel import Field, Session, SQLModel, and_, col, or_, select

from ..core.config import settings
from ..core.security import generate_passwd_hash
from ..models import (PasswordResetConfirmModel, User, UserCreate, UserProfile,
                      UserUpdate)
from ..utils.exceptions import (ResponseException, UserAlreadyExists,
                                UserNotFound)
from ..utils.validation import formatSorting
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def list(
        self,
        search: Optional[str] = None,
        sorting: Optional[str] = None
    ) -> List[User]:
        """Retrieve all data."""
        stmt = select(User)

        if search:
            stmt = stmt.where(
                or_(
                    col(User.first_name).icontains(search),
                    col(User.last_name).icontains(search),
                    col(User.email).icontains(search),
                    col(User.username).icontains(search),
                )
            )

        if sorting:
            xSort = formatSorting(User, sorting)
            stmt = stmt.order_by(text(xSort))

        return await self.get_all(stmt)

    async def get_by_id(self, id: int) -> Optional[User]:
        """Retrieve a data by its ID."""
        stmt = select(User).where(User.id == id)
        res = await self.get_one(stmt)

        if res is None:
            raise UserNotFound()

        return res

    async def create(self, obj: UserCreate) -> User:
        """Register a new data."""
        # validate basemodel
        db_dict = User.model_validate(obj)

        # generate hashed password
        db_dict.password = await generate_passwd_hash(obj.password)

        user = await self.add_one(db_dict)

        # auto create user profile
        await self.add_one(
            UserProfile(**{
                "role": "User",
                "user_id": user.id,
                "status_id": 3,  # Pending
            })
        )

        await self.session.refresh(user)

        # fix Pydantic serializer warnings Expected `str` but got `bytes`
        # convert bytes password to str password
        # user.password = str(user.password)
        return user

    async def edit(self, id: int, obj: UserUpdate) -> User:
        """Edit data."""
        # get data
        data_db = await self.get_by_id(id)

        # validate payload
        dump_data = obj.model_dump(exclude_unset=True)
        # update payload to data
        data_db.sqlmodel_update(dump_data)

        # process save data
        res = await self.add_one(data_db)
        return res

    async def delete(self, id: int) -> None:
        """Delete data."""
        data_db = await self.get_by_id(id)
        return await self.delete_one(data_db)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await self.get_one(stmt)

        if res is None:
            raise UserNotFound()

        return res

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        res = await self.get_one(stmt)

        if res is None:
            raise UserNotFound()

        return res

    async def verify_user(self, user: User) -> User:
        # if verify, update status=1, is_verified=True, verified_at=now()
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = settings.STATUS_USER_ACTIVE

        # process update data
        return await self.add_one(user)

    async def reset_password(self, user: User, payload: PasswordResetConfirmModel) -> User:
        # validate basemodel
        PasswordResetConfirmModel.model_validate(payload)

        # generate hashed password
        user.password = await generate_passwd_hash(payload.new_password)

        # process save data
        return await self.add_one(user)

    async def update_profile(self, user: User, payload: UserUpdate) -> User:
        # prepare update user
        user.sqlmodel_update(payload.model_dump(exclude_unset=True))

        if payload.profile:
            # prepare update profile
            user.profile.sqlmodel_update(payload.profile.model_dump(exclude_unset=True))

        # process save user
        return await self.add_one(user)

    async def update_photo_profile(self, user: User, file_path: str) -> User:

        user.profile.photo = file_path

        # process save
        return await self.add_one(user)
