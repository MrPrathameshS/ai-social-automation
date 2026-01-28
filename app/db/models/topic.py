from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    topic_text = Column(Text, nullable=False)

    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    source = Column(String(20), default="MANUAL")
    status = Column(String(20), default="NEW")

    brand = relationship("BrandProfile", back_populates="topics")

    contents = relationship(
        "ContentItem",
        back_populates="topic",
        cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=datetime.utcnow)

