from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from jose import JWTError, jwt


# =====================================================
# LOAD ENVIRONMENT
# =====================================================

load_dotenv()


# =====================================================
# JWT CONFIGURATION
# =====================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured."
    )

JWT_ALGORITHM = "HS256"

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =====================================================
# CREATE ACCESS TOKEN
# =====================================================

def create_access_token(
    user_id: int
) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )



# =====================================================
# DECODE ACCESS TOKEN
# =====================================================

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={
                "require_sub": True,
                "require_exp": True,
            },
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id.isdigit():
            raise ValueError("Invalid authentication token.")

        user_id = int(user_id)

        if user_id <= 0:
            raise ValueError("Invalid authentication token.")

        return user_id

    except (JWTError, ValueError, TypeError, OverflowError):
        raise ValueError("Invalid authentication token.") from None