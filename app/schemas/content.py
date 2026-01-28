from pydantic import BaseModel
from typing import Optional
from app.core.platform import Platform


class ContentGenerateRequest(BaseModel):
    topic_id: int
    platform: Platform
    category_id: Optional[int] = None

    class Config:
        use_enum_values = True
