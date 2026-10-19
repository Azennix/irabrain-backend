import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID"
)


def verify_google_id_token(
    credential: str
) -> dict:

    if not GOOGLE_CLIENT_ID:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID is not configured."
        )

    try:

        google_user = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

    except ValueError:

        raise ValueError(
            "Invalid Google authentication."
        )

    if google_user.get("iss") not in (
        "accounts.google.com",
        "https://accounts.google.com"
    ):
        raise ValueError(
            "Invalid Google token issuer."
        )

    google_sub = google_user.get("sub")
    email = google_user.get("email")

    if not google_sub or not email:
        raise ValueError(
            "Google account information is incomplete."
        )

    return {
        "google_sub": google_sub,
        "email": email.strip().lower(),
        "email_verified": bool(
            google_user.get("email_verified", False)
        ),
        "name": google_user.get("name"),
        "picture": google_user.get("picture"),
    }