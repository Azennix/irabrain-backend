import os

import resend
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "onboarding@resend.dev")


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is not configured.")

    if not EMAIL_FROM:
        raise RuntimeError("EMAIL_FROM is not configured.")

    resend.api_key = RESEND_API_KEY

    resend.Emails.send(
        {
            "from": EMAIL_FROM,
            "to": [to_email],
            "subject": subject,
            "text": body,
        }
    )