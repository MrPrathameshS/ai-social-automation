from sqlalchemy import Column, Integer, JSON, DateTime, String, ForeignKey
from datetime import datetime
from app.db.base import Base


class ApprovalBatch(Base):
    __tablename__ = "approval_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String(255), nullable=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=True)
    platform = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")
    filter_json = Column(JSON)
    decided_at = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
