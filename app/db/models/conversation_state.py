# app/models/conversation_state.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.db.base import Base


class ConversationState(Base):
    __tablename__ = "conversation_state"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("conversation_sessions.id"),
        nullable=False,
        unique=True,
    )

    topic = Column(String, nullable=True)

    challenge = Column(String, nullable=True)

    lesson = Column(String, nullable=True)

    angle = Column(String, nullable=True)

    tone = Column(String, nullable=True)

    step = Column(
        String,
        nullable=False,
        default="ASK_TOPIC",
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now(),
    )