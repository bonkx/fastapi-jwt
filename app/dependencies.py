# Defines dependencies used by the routers
from functools import lru_cache
from typing import Any, List

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from .core.config import Settings
from .core.database import get_session
from .core.redis import token_in_blocklist
from .core.security import decode_token
from .models import User
from .services.user_service import UserService
from .repositories.user_repo import UserRepository
from .utils.exceptions import (AccessTokenRequired, AccountNotVerified,
                               AccountSuspended, InsufficientPermission,
                               InvalidToken, RefreshTokenRequired)


@lru_cache
def get_settings():
    return Settings()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = await self.token_valid(token)
        if not token_data:
            raise InvalidToken()

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

        await self.verify_token_data(token_data)

        return token_data

    async def token_valid(self, token: str) -> dict:
        token_data = await decode_token(token)

        return token_data if token_data is not None else None

    async def verify_token_data(self, token_data):  # pragma: no cover
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    async def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    async def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    user_email = token_details["user"]["email"]

    repo = UserRepository(session)
    user = await UserService(repo).get_by_email(user_email)

    if user.profile.status_id in [settings.STATUS_USER_IN_ACTIVE, settings.STATUS_USER_SUSPENDED]:
        raise AccountSuspended()

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.profile.role.upper() in self.allowed_roles:
            return True

        raise InsufficientPermission()
