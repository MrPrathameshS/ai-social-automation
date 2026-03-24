from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class LinkedInPost(Base):
    __tablename__ = "linkedin_posts"

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    linkedin_post_urn = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)

    status = Column(String(50), nullable=False)

    error_message = Column(Text, nullable=True)
    error_type = Column(String(50), nullable=True)

    retry_count = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    published_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
