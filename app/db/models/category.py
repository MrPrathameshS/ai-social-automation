from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=True)
    is_system = Column(Boolean, default=False)

    brand = relationship("BrandProfile", back_populates="categories")
    rules = relationship("BrandRule", back_populates="category")

