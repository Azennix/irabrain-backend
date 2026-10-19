from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from database.database import Base


class LLMUsage(Base):

    __tablename__ = "llm_usage"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    request_id = Column(
        String(255),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    provider = Column(
        String(100),
        nullable=False
    )

    model = Column(
        String(255),
        nullable=False
    )

    input_tokens = Column(
        Integer,
        nullable=True
    )

    output_tokens = Column(
        Integer,
        nullable=True
    )

    cached_tokens = Column(
        Integer,
        nullable=True
    )

    reasoning_tokens = Column(
        Integer,
        nullable=True
    )

    total_tokens = Column(
        Integer,
        nullable=True
    )

    estimated_cost = Column(
        Float,
        nullable=True
    )

    latency = Column(
        Float,
        nullable=True
    )

    success = Column(
        Boolean,
        nullable=False,
        default=True
    )

    error = Column(
        String(2000),
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )