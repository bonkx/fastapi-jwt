from datetime import datetime, timedelta
from typing import List, Optional

from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.security import create_access_token, verify_password
from ..models import TokenSchema, UserLoginModel
from ..utils.exceptions import (AccountNotVerified, InvalidCredentials,
                                InvalidToken)
from .base import BaseService
from .user_service import UserService


class AuthService(BaseService):

    async def login_user(self, payload: UserLoginModel) -> TokenSchema:
        # get user data by email
        user = await UserService(self.session).get_by_email(payload.email)
        # print(user.password)

        # check user verify status
        if not user.is_verified:
            raise AccountNotVerified()

        # verify user's password
        password_valid = await verify_password(payload.password, user.password)
        if not password_valid:
            raise InvalidCredentials()

        access_token = await create_access_token(
            user_data={
                "email": user.email,
                "user_id": str(user.id),
                "role": user.profile.role,
            },
            # expiry=timedelta(seconds=5) # for DEV
        )

        refresh_token = await create_access_token(
            user_data={"email": user.email, "user_id": str(user.id)},
            refresh=True,
            expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        token = TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            user={"email": user.email, "id": str(user.id)}
        )

        return token

    # async def get_new_access_token(self, token_details: dict) -> TokenSchema:
    #     expiry_timestamp = token_details["exp"]

    #     if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
    #         new_access_token = create_access_token(user_data=token_details["user"])

    #         return JSONResponse(content={"access_token": new_access_token})

    #     raise InvalidToken()
