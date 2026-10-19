from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)

from database.database import Base


class SubscriptionModel(Base):

    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_subscriptions_user_id",
    ),
)

    subscription_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    tier = Column(
        String(32),
        nullable=False,
    )

    status = Column(
        String(32),
        nullable=False,
    )

    started_at = Column(
        DateTime,
        nullable=False,
    )

    current_period_started_at = Column(
        DateTime,
        nullable=False,
    )

    current_period_ends_at = Column(
        DateTime,
        nullable=False,
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