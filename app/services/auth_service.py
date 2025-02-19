from datetime import UTC, datetime, timedelta
from typing import List, Optional

from fastapi import BackgroundTasks, status
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.security import (create_access_token, create_url_safe_token,
                             verify_password)
from ..models import PasswordResetRequestModel, TokenSchema, UserLoginModel
from ..utils.exceptions import (AccountNotVerified, InvalidCredentials,
                                InvalidToken, UserNotFound)
from .base import BaseService
from .mail_service import MailService
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

    async def get_new_access_token(self, token_details: dict) -> TokenSchema:
        expiry_timestamp = token_details["exp"]

        if datetime.fromtimestamp(expiry_timestamp, tz=UTC) > datetime.now(UTC):
            # new_access_token = await create_access_token(user_data=token_details["user"])
            # return JSONResponse(content={"access_token": new_access_token})

            access_token = await create_access_token(user_data=token_details["user"])

            refresh_token = await create_access_token(
                user_data=token_details["user"],
                refresh=True,
                expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            )

            token = TokenSchema(
                detail="Refresh Token successful",
                access_token=access_token,
                refresh_token=refresh_token,
                user=token_details["user"]
            )

            return token

        raise InvalidToken()

    async def password_reset_request(
        self,
        email_data: PasswordResetRequestModel,
        background_tasks: BackgroundTasks,
    ) -> JSONResponse:
        email = email_data.email

        # get user
        await UserService(self.session).get_by_email(email)

        expiration_datetime = datetime.now(UTC) + timedelta(seconds=1800)  # pragma: no cover # 30 minutes
        token = await create_url_safe_token({  # pragma: no cover
            "email": email,
            "exp": expiration_datetime,
            "action": "resend_verification_link"
        })
        # print("token encode:", token)
        link = f"{settings.DOMAIN}/account/password-reset-confirm/{token}"  # pragma: no cover
        # print("link:", link)

        email_payload = {  # pragma: no cover
            "subject": "Reset Your Password",
            "emails": [
                email
            ],
            "body": {
                "name": email,
                "action_url": link,
            }
        }

        # send email
        await MailService(background_tasks).send__email(  # pragma: no cover
            email_payload=email_payload,
            template_name="request_reset_password_email.html"
        )

        return JSONResponse(  # pragma: no cover
            content={
                "detail": "Please check your email for instructions to reset your password",
            },
            status_code=status.HTTP_200_OK,
        )
