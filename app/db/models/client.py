from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    brands = relationship("BrandProfile", back_populates="client", cascade="all, delete-orphan")
