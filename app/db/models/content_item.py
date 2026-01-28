from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.core.platform import Platform


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)

    platform = Column(
        String(50),
        nullable=False
    )
    content_type = Column(String(50), nullable=False)
    content_text = Column(Text, nullable=True)

    status = Column(String(50), default="DRAFT")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ Publishing fields
    published_at = Column(DateTime(timezone=True), nullable=True)
    publish_error = Column(Text, nullable=True)
    linkedin_post_urn = Column(String, nullable=True)

    # ⏰ Scheduling
    scheduled_for = Column(DateTime(timezone=True), nullable=True)

    # 🔁 Retry + Backoff (ADD THESE)
    retry_count = Column(Integer, default=0, nullable=False)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)

    brand = relationship("BrandProfile", back_populates="content_items")
    topic = relationship("Topic", back_populates="contents")

    schedules = relationship(
        "Schedule",
        back_populates="content_item",
        cascade="all, delete-orphan"
    )
