import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME)


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:

    if not SMTP_USERNAME:
        raise RuntimeError("SMTP_USERNAME is not configured.")

    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is not configured.")

    if not EMAIL_FROM:
        raise RuntimeError("EMAIL_FROM is not configured.")

    message = EmailMessage()

    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=20,
    ) as server:

        server.starttls()

        server.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        server.send_message(message)