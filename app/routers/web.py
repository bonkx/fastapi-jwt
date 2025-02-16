from datetime import datetime
from typing import Annotated, Any, List

import jwt
from fastapi import (APIRouter, BackgroundTasks, Depends, FastAPI, Query,
                     Request, status)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse, RedirectResponse

from ..core import config
from ..core.database import get_session
from ..core.email import send_email_background
from ..core.security import decode_url_safe_token
from ..dependencies import get_settings
from ..services.user_service import UserService

router = APIRouter()
account_router = APIRouter()

# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
async def root():
    return {"message": "Server is Running..."}


@router.get("/docs", include_in_schema=False)
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
    # TODO:
    # check validate token
    try:
        msg = "Account Verification Successful!"

        # invalid token
        # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImpvaG5kb2UxMjNAZmFzdGFwaS5jb20iLCJleHAiOjE3Mzk3MDY0MTR9.e1WKE2Z9n-1-onRhfSLMiuZVZeu2AnXMo3v_U_gt3Cc

        # valid token
        # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImpvaG5kb2UxMjNAZmFzdGFwaS5jb20iLCJleHAiOjE3Mzk3MTk4MTB9.SFevQKVENwm3Q99g8bCNSYESnXIbD0Sa39Wo9SnoQXk

        decode_token = await decode_url_safe_token(token)
        print("decode_token:", decode_token)

        # get user data
        user = await UserService(session).get_by_email(decode_token["email"])
        # print(user)
        # print("user.is_verified:", user.is_verified)
        if user.is_verified:
            msg = "Account already verified"
        else:
            await UserService(session).verify_user(user)
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
async def resend_verification_link(request: Request, token: str):
    # TODO:
    # check validate token
    # if verify, send verification email

    msg = "Verification email has been successfully sent"

    context = {
        "page_title": "Request a new verification email",
        "msg": msg
    }

    return templates.TemplateResponse(
        request=request, name="verification_done.html", context=context
    )
