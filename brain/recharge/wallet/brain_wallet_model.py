from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, Numeric

from database.database import Base


class BrainWalletModel(Base):
    __tablename__ = "brain_wallets"

    user_id = Column(
        Integer,
        primary_key=True,
    )

    current_balance = Column(
        Numeric(20, 4),
        nullable=False,
        default=0,
    )

    lifetime_purchased = Column(
        Numeric(20, 4),
        nullable=False,
        default=0,
    )

    lifetime_consumed = Column(
        Numeric(20, 4),
        nullable=False,
        default=0,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )