from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.email import send_email_background
from ..dependencies import RefreshTokenBearer
from ..models import (EmailSchema, TokenSchema, UserCreate, UserLoginModel,
                      UserSchema)
from ..services.auth_service import AuthService
from ..services.mail_service import MailService
from ..services.user_service import UserService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_200_OK)
async def create_user_account(
    background_tasks: BackgroundTasks,
    user_data: UserCreate,
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


# @router.post("/refresh_token")
# async def get_new_access_token(
#     token_details: dict = Depends(RefreshTokenBearer()),
#     session: AsyncSession = Depends(get_session),
# ):
#     return await AuthService(session).get_new_access_token(token_details)


# @auth_router.get("/logout")
# async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
#     jti = token_details["jti"]

#     await add_jti_to_blocklist(jti)

#     return JSONResponse(
#         content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
#     )


@router.post("/email", responses={200: {"detail": "Email has been sent"}})
async def simple_send_email(background_tasks: BackgroundTasks, email: EmailSchema) -> JSONResponse:
    template_name = "common_email.html"
    send_email_background(background_tasks, email, template_name)
    return JSONResponse(status_code=200, content={"detail": "Email has been sent"})
