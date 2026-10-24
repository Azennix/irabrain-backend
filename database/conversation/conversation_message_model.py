from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database.database import Base


class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    conversation_id = Column(String(100), nullable=True, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    visual_data = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
