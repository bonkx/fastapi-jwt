from datetime import UTC, datetime, timedelta

from ..core.config import settings
from ..core.email import send_email_background
from ..core.security import create_url_safe_token
from ..models import EmailSchema, User
from .base import EmailBackgroundTasksMixin


class MailService(EmailBackgroundTasksMixin):

    async def send__email(self, email_payload: dict, template_name: str) -> None:
        email = EmailSchema(**email_payload)
        send_email_background(self.background_tasks, email, template_name)

    async def send_verification_email(self, new_user: User) -> None:
        expiration_datetime = datetime.now(UTC) + timedelta(seconds=3600)  # 60 minutes
        token = await create_url_safe_token({"email": new_user.email, "exp": expiration_datetime})
        # print("token encode:", token)
        link = f"{settings.DOMAIN}/account/verify/{token}"
        # print("link:", link)

        token_resend = await create_url_safe_token({"email": new_user.email, "action": "resend_verification_link"})
        link_resend = f"{settings.DOMAIN}/account/resend-verification/{token_resend}"

        email_payload = {
            "subject": "Verify your email address",
            "emails": [
                new_user.email
            ],
            "body": {
                "name": new_user.name,
                "action_url": link,
                "action_resend_url": link_resend,
            }
        }
        email = EmailSchema(**email_payload)
        template_name = "verification_email.html"
        send_email_background(self.background_tasks, email, template_name)
