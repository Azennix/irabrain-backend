from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric, String

from database.database import Base


class PaymentModel(Base):
    __tablename__ = "payments"

    payment_id = Column(
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

    amount = Column(
        Numeric(20, 4),
        nullable=False,
    )

    currency = Column(
        String(8),
        nullable=False,
    )

    status = Column(
        String(32),
        nullable=False,
    )

    provider = Column(
        String(32),
        nullable=False,
    )

    provider_order_id = Column(
        String(255),
        nullable=False,
        index=True,
    )

    provider_payment_id = Column(
        String(255),
        nullable=True,
        unique=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )