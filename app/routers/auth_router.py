from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.email import send_email_background
from ..core.redis import add_jti_to_blocklist
from ..dependencies import AccessTokenBearer, RefreshTokenBearer
from ..repositories.user_repo import UserRepository
from ..schemas.auth_schema import (LoginSchema, PasswordResetSchema, TokenSchema)
from ..schemas.email_schema import EmailSchema
from ..schemas.user_schema import UserSchema, UserCreateSchema
from ..services.auth_service import AuthService
from ..services.mail_service import MailService
from ..services.user_service import UserService
from ..utils.response import ResponseDetailSchema

router = APIRouter()


async def get_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    repo = UserRepository(session)
    return AuthService(repo)


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


@router.post("/register", status_code=status.HTTP_200_OK)
async def create_user_account(
    user_data: UserCreateSchema,
    background_tasks: BackgroundTasks,
    userSrv: UserService = Depends(get_user_service)
):
    new_user = await userSrv.create(user_data)

    if new_user:  # pragma: no cover
        # Send link verification email
        await MailService(background_tasks).send_verification_email(new_user)

    return JSONResponse(content={  # pragma: no cover
        "detail": "Account Created! Check email to verify your account",
        "user": jsonable_encoder(UserSchema.model_validate(new_user))
    })


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_account(
    payload: LoginSchema,
    srv: AuthService = Depends(get_service)
) -> TokenSchema:
    return await srv.login_user(payload)


@router.post("/refresh-token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer()),
    srv: AuthService = Depends(get_service)
) -> TokenSchema:
    return await srv.get_new_access_token(token_details)


@router.post("/password-reset-request")
async def password_reset_request(
    payload: PasswordResetSchema,
    background_tasks: BackgroundTasks,
    srv: AuthService = Depends(get_service)
) -> JSONResponse:
    return await srv.password_reset_request(payload, background_tasks)


@router.get("/logout", include_in_schema=False)
@router.post("/logout", response_model=ResponseDetailSchema)
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())) -> JSONResponse:
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
