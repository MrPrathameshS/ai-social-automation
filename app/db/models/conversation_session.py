# app/models/conversation_session.py

from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True)

    status = Column(String, nullable=False, default="ACTIVE")

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now(),
    )