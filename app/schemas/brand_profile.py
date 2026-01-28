from pydantic import BaseModel
from typing import Optional


class BrandProfileBase(BaseModel):
    brand_name: str
    client_id: int
    platform: str
    page_id: Optional[str] = None
    tone_description: Optional[str] = None
    audience_description: Optional[str] = None
    writing_style: Optional[str] = None
    do_not_use: Optional[str] = None
    learned_insights: Optional[str] = None
    is_active: Optional[bool] = True
    approval_required: Optional[bool] = True
    voice_version: Optional[str] = "v1"


class BrandProfileCreate(BrandProfileBase):
    pass


class BrandProfileUpdate(BaseModel):
    brand_name: Optional[str] = None
    platform: Optional[str] = None
    page_id: Optional[str] = None
    tone_description: Optional[str] = None
    audience_description: Optional[str] = None
    writing_style: Optional[str] = None
    do_not_use: Optional[str] = None
    learned_insights: Optional[str] = None
    is_active: Optional[bool] = None
    approval_required: Optional[bool] = None
    voice_version: Optional[str] = None


class BrandProfileOut(BrandProfileBase):
    id: int

    class Config:
        orm_mode = True
