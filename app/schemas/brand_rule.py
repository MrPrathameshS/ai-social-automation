from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrandRuleBase(BaseModel):
    platform: Optional[str] = None
    category_id: Optional[int] = None
    rule_type: str
    rule_text: str


class BrandRuleCreate(BrandRuleBase):
    pass


class BrandRuleResponse(BrandRuleBase):
    id: int
    is_active: bool
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True
