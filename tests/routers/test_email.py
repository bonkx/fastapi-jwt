
from app.core.email import fm

from . import pytest, pytestmark


async def test_send_email(client, api_prefix):
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        payload = {
            "subject": "Test Email",
            "emails": [
                "user@example.com"
            ],
            "body": {
                "title": "Hello World",
                "name": "John Doe"
            }
        }
        url = f"{api_prefix}/auth/email"
        response = await client.post(url, json=payload)
        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0]['from'] == "FastAPI <no-reply@example.com>"
        assert outbox[0]['To'] == "user@example.com"
