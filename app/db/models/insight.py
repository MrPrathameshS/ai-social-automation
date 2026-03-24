# app/db/models/insight.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

from app.db.base import Base


class Insight(Base):

    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("conversation_sessions.id"),
        nullable=False,
    )

    topic = Column(String, nullable=True)

    challenge = Column(String, nullable=True)

    lesson = Column(String, nullable=True)

    angle = Column(String, nullable=True)

    tone = Column(String, nullable=True)

    tags = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )