from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric

from database.database import Base


class FreeBrainEntitlementModel(Base):
    __tablename__ = "free_brain_entitlements"

    user_id = Column(
        Integer,
        primary_key=True,
    )

    allowance = Column(
        Numeric(20, 4),
        nullable=False,
    )

    consumed = Column(
        Numeric(20, 4),
        nullable=False,
        default=0,
    )

    reset_interval_hours = Column(
        Integer,
        nullable=False,
    )

    period_started_at = Column(
        DateTime,
        nullable=False,
    )

    next_reset_at = Column(
        DateTime,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )