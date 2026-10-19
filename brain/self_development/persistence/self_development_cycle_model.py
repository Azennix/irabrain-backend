from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String

from database.database import Base


class SelfDevelopmentCycleModel(Base):

    __tablename__ = "self_development_cycles"

    cycle_id = Column(
        String(100),
        primary_key=True,
    )

    user_id = Column(
        Integer,
        nullable=True,
        index=True,
    )
    system_id = Column(
        String(100),
        ForeignKey("system_identities.system_id"),
        nullable=True,
        index=True,
)

    improvement_id = Column(
        String(100),
        nullable=False,
        index=True,
    )

    stage = Column(
        String(50),
        nullable=False,
    )

    context = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    result = Column(
        JSON,
        nullable=True,
    )

    error = Column(
        String(2000),
        nullable=True,
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