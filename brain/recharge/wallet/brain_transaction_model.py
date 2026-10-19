from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)

from database.database import Base


class BrainTransactionModel(Base):
    __tablename__ = "brain_transactions"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    transaction_id = Column(
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

    transaction_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    units = Column(
        Numeric(20, 4),
        nullable=False,
    )

    reference_id = Column(
        String(255),
        nullable=True,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
    )

    metadata_json = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    __table_args__ = (
        Index(
            "uq_brain_transactions_reference_id_not_null",
            "reference_id",
            unique=True,
            postgresql_where=reference_id.isnot(None),
        ),
    )