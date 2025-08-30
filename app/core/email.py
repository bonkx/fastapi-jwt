# Defines functions for sending emails.

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from ..schemas.email_schema import EmailSchema

from .config import settings

email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER='./templates'
)


fm = FastMail(email_conf)


def send_email_background(
    background_tasks: BackgroundTasks,
    email: EmailSchema,
    template_name: str,
):
    message = MessageSchema(
        subject=email.model_dump().get("subject"),
        recipients=email.model_dump().get("emails"),
        template_body=email.model_dump().get("body"),
        subtype=MessageType.html,
    )

    # fm = FastMail(email_conf)

    background_tasks.add_task(
        fm.send_message, message, template_name=template_name)


# async def send_email_async(
#     email: EmailSchema,
#     template_name: str
# ):
#     message = MessageSchema(
#         subject=email.model_dump().get("subject"),
#         recipients=email.model_dump().get("emails"),
#         template_body=email.model_dump().get("body"),
#         subtype=MessageType.html,
#     )

#     # fm = FastMail(email_conf)

#     await fm.send_message(message, template_name=template_name)
