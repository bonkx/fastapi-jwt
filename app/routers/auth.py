from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from ..core.database import get_session
from ..core.email import send_email_background
from ..models import EmailSchema, UserCreate, UserSchema
from ..services.mail_service import MailService
from ..services.user_service import UserService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_200_OK)
async def create_user_Account(
    background_tasks: BackgroundTasks,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create user account using email, username, first_name, last_name
    params:
        user_data: UserCreate
    """

    new_user = await UserService(session).create(user_data)

    if new_user:
        # Send link verification email
        await MailService(background_tasks).send_verification_email(new_user)

    return {
        "detail": "Account Created! Check email to verify your account",
        "user": UserSchema(**new_user.model_dump()),
    }


@router.post("/email", responses={200: {"detail": "Email has been sent"}})
async def simple_send_email(background_tasks: BackgroundTasks, email: EmailSchema) -> JSONResponse:
    template_name = "common_email.html"
    send_email_background(background_tasks, email, template_name)
    return JSONResponse(status_code=200, content={"detail": "Email has been sent"})
