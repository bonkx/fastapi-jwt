from fastapi import APIRouter, Depends, FastAPI, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..models import UserCreate, UserSchema
from ..services.user_service import UserService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_200_OK)
async def create_user_Account(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create user account using email, username, first_name, last_name
    params:
        user_data: UserCreate
    """

    new_user = await UserService(session).create(user_data)

    # token = create_url_safe_token({"email": email})

    # link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    # html = f"""
    # <h1>Verify your Email</h1>
    # <p>Please click this <a href="{link}">link</a> to verify your email</p>
    # """

    # emails = [email]

    # subject = "Verify Your email"

    # send_email.delay(emails, subject, html)

    return {
        "detail": "Account Created! Check email to verify your account",
        "user": UserSchema(**new_user.model_dump()),
    }

# @router.post("/send_mail")
# async def send_mail(emails: EmailModel):
#     emails = emails.addresses

#     html = "<h1>Welcome to the app</h1>"
#     subject = "Welcome to our app"

#     send_email.delay(emails, subject, html)

#     return {"message": "Email sent successfully"}
