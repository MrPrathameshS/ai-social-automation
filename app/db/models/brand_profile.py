from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    platform = Column(String(50), nullable=False)
    page_id = Column(String(255), nullable=True)

    # 🔑 LinkedIn credentials (ADDED)
    linkedin_access_token = Column(Text, nullable=True)
    linkedin_author_urn = Column(String(255), nullable=True)

    tone_description = Column(Text, nullable=True)
    audience_description = Column(Text, nullable=True)
    writing_style = Column(Text, nullable=True)
    do_not_use = Column(Text, nullable=True)
    learned_insights = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    approval_required = Column(Boolean, default=True)
    voice_version = Column(String(50), default="v1")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # =========================
    # Relationships
    # =========================

    client = relationship("Client", back_populates="brands")

    topics = relationship(
        "Topic",
        back_populates="brand",
        cascade="all, delete-orphan"
    )

    content_items = relationship(
        "ContentItem",
        back_populates="brand",
        cascade="all, delete-orphan"
    )

    prompts = relationship(
        "PromptTemplate",
        back_populates="brand",
        cascade="all, delete-orphan"
    )

    categories = relationship(
        "Category",
        back_populates="brand",
        cascade="all, delete-orphan"
    )

    rules = relationship(
        "BrandRule",
        back_populates="brand",
        cascade="all, delete-orphan"
    )
