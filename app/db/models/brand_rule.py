from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class BrandRule(Base):
    __tablename__ = "brand_rules"

    id = Column(Integer, primary_key=True, index=True)

    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    platform = Column(String(50), nullable=True)   # linkedin, instagram, etc
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    rule_type = Column(String(50), nullable=False)
    rule_text = Column(Text, nullable=False)

    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    brand = relationship("BrandProfile", back_populates="rules")
    category = relationship("Category", back_populates="rules")
