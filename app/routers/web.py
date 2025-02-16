from typing import Annotated, Any, List

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
from ..dependencies import get_settings
from ..models import EmailSchema, UserCreate, UserSchema
from ..services.mail_service import MailService
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
async def verify_verification_link(request: Request, token: str):
    # TODO:
    # check validate token
    # if verify, update status user

    # msg = "Oops... Wrong Token"
    msg = "Account Verification Successful!"

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
