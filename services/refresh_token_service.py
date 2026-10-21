import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from database.refresh_token_model import RefreshToken
from database.user_repository import UserRepository


SESSION_LIFETIME_DAYS = 30


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class RefreshTokenService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int) -> tuple[str, datetime]:
        user = UserRepository(self.db).get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("Cannot create a session for this user.")

        raw_token = secrets.token_urlsafe(48)
        expires_at = utc_now() + timedelta(days=SESSION_LIFETIME_DAYS)

        self.db.add(
            RefreshToken(
                user_id=user_id,
                token_hash=hash_token(raw_token),
                expires_at=expires_at,
            )
        )
        self.db.flush()

        return raw_token, expires_at

    def rotate(
        self,
        raw_token: str,
    ) -> tuple[int, str, datetime] | None:
        record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == hash_token(raw_token))
            .with_for_update()
            .first()
        )

        now = utc_now()

        if (
            record is None
            or record.revoked_at is not None
            or record.expires_at <= now
        ):
            return None

        user = UserRepository(self.db).get_by_id(record.user_id)

        if user is None or not user.is_active:
            record.revoked_at = now
            self.db.flush()
            return None

        user_id = record.user_id
        original_expiry = record.expires_at
        record.revoked_at = now

        replacement = secrets.token_urlsafe(48)
        self.db.add(
            RefreshToken(
                user_id=user_id,
                token_hash=hash_token(replacement),
                expires_at=original_expiry,
            )
        )
        self.db.flush()

        return user_id, replacement, original_expiry

    def revoke(self, raw_token: str) -> bool:
        record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == hash_token(raw_token))
            .with_for_update()
            .first()
        )

        if record is None or record.revoked_at is not None:
            return False

        record.revoked_at = utc_now()
        self.db.flush()
        return True
