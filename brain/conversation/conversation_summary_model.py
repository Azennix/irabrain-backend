from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from database.database import Base


class ConversationSummaryModel(Base):

    __tablename__ = "conversation_summaries"

    summary_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    conversation_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    summary = Column(
        Text,
        nullable=False
    )

    summarized_until_message_id = Column(
        Integer,
        nullable=False
    )

    message_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    version = Column(
        Integer,
        nullable=False,
        default=1
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