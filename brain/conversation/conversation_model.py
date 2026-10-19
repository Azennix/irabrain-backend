from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database.database import Base


class ConversationModel(Base):

    __tablename__ = "conversations"

    conversation_id = Column(
        String(100),
        primary_key=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )