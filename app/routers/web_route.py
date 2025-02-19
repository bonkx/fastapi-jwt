from datetime import datetime
from typing import Annotated, Any, List

import jwt
from fastapi import (APIRouter, BackgroundTasks, Depends, FastAPI, Query,
                     Request, status)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core import config
from ..core.database import get_session
from ..core.redis import add_jti_to_blocklist, token_in_blocklist
from ..core.security import decode_url_safe_token
from ..dependencies import get_settings
from ..models import PasswordResetConfirmModel
from ..services.mail_service import MailService
from ..services.user_service import UserService
from ..utils.exceptions import InvalidToken

home_router = APIRouter()
account_router = APIRouter()

# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@home_router.get("/", include_in_schema=False)
async def root():
    return {"message": "Server is Running..."}


@home_router.get("/docs", include_in_schema=False)
async def docs(settings: Annotated[config.Settings, Depends(get_settings)]):
    # """
    # # Redirect
    # to documentation (`/docs/`).
    # """
    return RedirectResponse(url=f"{settings.API_PREFIX}/docs/")


@account_router.get("/verify/{token}", response_class=HTMLResponse)
async def verify_verification_link(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        msg = "Account Verification Successful!"

        # check validate token
        decode_token = await decode_url_safe_token(token)
        # print("decode_token:", decode_token)

        # get user data by email
        user = await UserService(session).get_by_email(decode_token["email"])
        # print(user)
        # print("user.is_verified:", user.is_verified)
        if user.is_verified:  # pragma: no cover
            msg = "Account already verified"
        else:
            await UserService(session).verify_user(user)  # pragma: no cover
    except Exception as e:
        print(str(e))
        msg = "Oops... Invalid Token"

    context = {
        "page_title": "Account Verification",
        "msg": msg
    }
    return templates.TemplateResponse(
        request=request, name="verification_done.html", context=context
    )


@account_router.get("/resend-verification/{token}", response_class=HTMLResponse)
async def resend_verification_link(
    background_tasks: BackgroundTasks,
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        msg = "New verification email has been successfully sent"

        # check validate token
        decode_token = await decode_url_safe_token(token)
        # print("decode_token:", decode_token)

        # get user data by email
        user = await UserService(session).get_by_email(decode_token["email"])
        # print(user)

        if user.is_verified:  # pragma: no cover
            msg = "Account already verified"
        else:
            # if user not verified, send verification email
            await MailService(background_tasks).send_verification_email(user)  # pragma: no cover
    except Exception as e:
        print(str(e))
        msg = "Oops... Invalid Token"

    context = {
        "page_title": "Request a new verification email",
        "msg": msg
    }

    return templates.TemplateResponse(
        request=request, name="verification_done.html", context=context
    )


@account_router.get("/password-reset-confirm/{token}", response_class=HTMLResponse)
async def password_reset_confirm(
    request: Request,
    token: str,
):
    context = {
        "page_title": "Request a new verification email",
        "method": "GET",
        "status": "OK",
        "msg": "Please change your password"
    }
    try:
        # check validate token
        decode_token = await decode_url_safe_token(token)
        # print("decode_token:", decode_token)

        if decode_token["action"] != "resend_verification_link":
            raise Exception("Oops... Invalid Token")

        if await token_in_blocklist(decode_token["jti"]):
            raise Exception("Token is invalid Or expired")
    except Exception as e:
        print(str(e))
        context["status"] = "Error"
        context["msg"] = f"{str(e)}"

    return templates.TemplateResponse(
        request=request, name="password_reset_confirm.html", context=context
    )


@account_router.post("/password-reset-confirm/{token}", response_class=HTMLResponse)
async def request_password_reset(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session),
):
    context = {
        "method": "POST",
        "status": "OK",
        "msg": "Password reset Successfully"
    }
    try:
        # check validate token
        decode_token = await decode_url_safe_token(token)
        # print("decode_token:", decode_token)

        if decode_token["action"] != "resend_verification_link":
            raise Exception("Oops... Invalid Token")

        # get user data by email
        user = await UserService(session).get_by_email(decode_token["email"])

        form_data = await request.form()
        payload = {
            "new_password": form_data.get("new_password"),
            "confirm_new_password": form_data.get("confirm_new_password")
        }

        res = await UserService(session).reset_password(user, PasswordResetConfirmModel(**payload))
        if res:
            # blacklist token
            await add_jti_to_blocklist(decode_token["jti"])
    except ValidationError as e:
        print(str(e))
        context["status"] = "Error"
        context["msg"] = "Passwords did not match or check length of your password again."
    except Exception as e:
        print(str(e))
        context["status"] = "Error"
        # context["msg"] = "Error occured during password reset."
        context["msg"] = str(e)

    return templates.TemplateResponse(
        request=request, name="password_reset_confirm.html", context=context
    )
