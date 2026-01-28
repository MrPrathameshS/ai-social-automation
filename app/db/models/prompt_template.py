from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    platform = Column(String, nullable=False)
    version = Column(Integer, default=1)
    prompt_text = Column(Text, nullable=False)
    mutation_reason = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("BrandProfile", back_populates="prompts")
