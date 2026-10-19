from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from database.database import Base


class AuditEventModel(Base):
    __tablename__ = "self_development_audit_events"

    event_id = Column(String(100), primary_key=True)
    cycle_id = Column(
        String(100),
        nullable=False,
        index=True,
    )
    system_id = Column(
        String(100),
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer,
        nullable=True,
        index=True,
    )
    event_type = Column(
        String(100),
        nullable=False,
        index=True,
    )
    action = Column(
        String(100),
        nullable=False,
    )
    stage = Column(
        String(50),
        nullable=True,
    )
    outcome = Column(
        String(50),
        nullable=False,
    )
    details = Column(
        JSON,
        nullable=False,
        default=dict,
    )
    created_at = Column(
        DateTime,
        nullable=False,
    )