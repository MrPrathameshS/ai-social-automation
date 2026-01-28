from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.base import Base


class PostingStrategy(Base):
    __tablename__ = "posting_strategies"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    strategy_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
