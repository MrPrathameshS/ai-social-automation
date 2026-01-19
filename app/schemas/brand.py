from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    brand_name: str
    tone_description: Optional[str] = None
    audience_description: Optional[str] = None
    writing_style: Optional[str] = None
    do_not_use: Optional[str] = None
    platform: str


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    brand_name: Optional[str] = None
    tone_description: Optional[str] = None
    audience_description: Optional[str] = None
    writing_style: Optional[str] = None
    do_not_use: Optional[str] = None
    platform: Optional[str] = None
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    id: int
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # correct for Pydantic v2
