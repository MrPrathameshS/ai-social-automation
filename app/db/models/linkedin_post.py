from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class LinkedInPost(Base):
    __tablename__ = "linkedin_posts"

    id = Column(Integer, primary_key=True, index=True)

    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    linkedin_post_urn = Column(String(255), nullable=False, unique=True)
    text = Column(Text, nullable=False)

    status = Column(String(50), default="published")  # published | failed
    error_message = Column(Text, nullable=True)

    published_at = Column(DateTime(timezone=True), server_default=func.now())
