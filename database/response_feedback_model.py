from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.database import Base


class ResponseFeedback(Base):

    __tablename__ = "response_feedback"

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

    conversation_id = Column(
        String(255),
        nullable=True,
        index=True,
    )

    message_id = Column(
        String(255),
        nullable=False,
        index=True,
    )

    rating = Column(
        String(20),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )