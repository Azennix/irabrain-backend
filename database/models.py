from datetime import datetime

from sqlalchemy import Column, String,  DateTime, Float, JSON, Integer, UniqueConstraint

from database.database import Base
from sqlalchemy import (
    Column,
    String,
    Float,
    JSON,
    Integer,
    UniqueConstraint
)


class MemoryEntity(Base):

    __tablename__ = "memories"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category",
            "key",
            name="uq_memory_user_category_key"
        ),
    )

    memory_id = Column(String, primary_key=True)

    user_id = Column(Integer, nullable=False)

    category = Column(String, nullable=False)

    key = Column(String, nullable=False)

    value = Column(String, nullable=False)

    embedding = Column(JSON, nullable=True)

    association_embedding = Column(JSON, nullable=True)

    confidence = Column(Float, nullable=False)


class NoteEntity(Base):
    __tablename__ = "notes"

    note_id = Column(String, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

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



class ProjectEntity(Base):

    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)

    user_id = Column(Integer, nullable=False)

    name = Column(String, nullable=False)

    description = Column(String, nullable=True)

    status = Column(String, nullable=False, default="active")

class GoalEntity(Base):
    __tablename__ = "project_goals"

    goal_id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")

class ProjectTaskEntity(Base):
    __tablename__ = "project_tasks"

    task_id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    goal_id = Column(String, nullable=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")



class ProjectDecisionEntity(Base):
    __tablename__ = "project_decisions"

    decision_id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)