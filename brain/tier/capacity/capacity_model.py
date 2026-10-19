from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric, String

from database.database import Base


class TierBrainCapacityModel(Base):
    __tablename__ = "tier_brain_capacities"

    user_id = Column(
        Integer,
        primary_key=True,
    )

    tier = Column(
        String(32),
        nullable=False,
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

    period_started_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    period_ends_at = Column(
        DateTime(timezone=True),
        nullable=False,
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