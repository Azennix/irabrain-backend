from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String

from database.database import Base


class SystemIdentityModel(Base):

    __tablename__ = "system_identities"

    system_id = Column(
        String(100),
        primary_key=True,
    )

    name = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )