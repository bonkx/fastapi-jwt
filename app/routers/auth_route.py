from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.email import send_email_background
from ..core.redis import add_jti_to_blocklist
from ..dependencies import AccessTokenBearer, RefreshTokenBearer
from ..models import (EmailSchema, PasswordResetRequestModel, TokenSchema,
                      UserCreate, UserLoginModel, UserSchema)
from ..services.auth_service import AuthService
from ..services.mail_service import MailService
from ..services.user_service import UserService
from ..utils.response import ResponseDetailSchema

router = APIRouter()


@router.post("/register", status_code=status.HTTP_200_OK)
async def create_user_account(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    new_user = await UserService(session).create(user_data)

    if new_user:  # pragma: no cover
        # Send link verification email
        await MailService(background_tasks).send_verification_email(new_user)

    return JSONResponse(content={  # pragma: no cover
        "detail": "Account Created! Check email to verify your account",
        "user": jsonable_encoder(UserSchema.model_validate(new_user))
    })


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_account(
    payload: UserLoginModel,
    session: AsyncSession = Depends(get_session),
) -> TokenSchema:
    return await AuthService(session).login_user(payload)


@router.post("/refresh-token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    return await AuthService(session).get_new_access_token(token_details)


@router.post("/password-reset-request")
async def password_reset_request(
    payload: PasswordResetRequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    return await AuthService(session).password_reset_request(payload, background_tasks)


@router.get("/logout", include_in_schema=False)
@router.post("/logout", response_model=ResponseDetailSchema)
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    # add jti in blocklist redis
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"detail": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )


@router.post("/email", responses={200: {"detail": "Email has been sent"}})
async def simple_send_email(background_tasks: BackgroundTasks, email: EmailSchema) -> JSONResponse:
    template_name = "common_email.html"
    send_email_background(background_tasks, email, template_name)
    return JSONResponse(status_code=200, content={"detail": "Email has been sent"})
