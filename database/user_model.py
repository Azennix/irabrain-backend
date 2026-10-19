from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from database.database import Base
from brain.tier.models import BrainTier


class User(Base):

    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    full_name = Column(
        String(255),
        nullable=True
)

    email = Column(
        String(320),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=True
    )

    google_sub = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    email_verified = Column(
        Boolean,
        nullable=False,
        default=False
    )

    # =====================================================
    # EMAIL VERIFICATION CODE
    # =====================================================

    email_verification_code_hash = Column(
        String(255),
        nullable=True
    )

    email_verification_code_expires_at = Column(
        DateTime,
        nullable=True
    )

    # =====================================================
    # OLD VERIFICATION LINK FIELDS
    # Keep temporarily for migration compatibility
    # =====================================================

    email_verification_token_hash = Column(
        String(255),
        nullable=True
    )

    email_verification_expires_at = Column(
        DateTime,
        nullable=True
    )

    # =====================================================
    # ACCOUNT
    # =====================================================

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    brain_tier = Column(
        String(32),
        nullable=False,
        default=BrainTier.FREE.value
    )