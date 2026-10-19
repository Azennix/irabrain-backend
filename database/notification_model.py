from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from database.database import Base


class NotificationEntity(Base):

    __tablename__ = "notifications"

    notification_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    type = Column(
        String(50),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    read_at = Column(
        DateTime,
        nullable=True
    )