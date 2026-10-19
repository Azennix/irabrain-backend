from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
)

from database.database import Base


class BrainSettlementModel(Base):
    __tablename__ = "brain_settlements"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    request_id = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    total_units = Column(
        Numeric(20, 4),
        nullable=False,
    )

    free_units = Column(
        Numeric(20, 4),
        nullable=False,
    )

    paid_units = Column(
        Numeric(20, 4),
        nullable=False,
    )

    calculation_version = Column(
        String(100),
        nullable=False,
    )

    basis = Column(
        String(100),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )