# app/models/conversation_message.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.db.base import Base


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("conversation_sessions.id"),
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
    )  # user / assistant / system

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )