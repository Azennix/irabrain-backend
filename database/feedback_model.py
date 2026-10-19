from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.database import Base


class Feedback(Base):

    __tablename__ = "feedback"

    feedback_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    feedback_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    message = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )