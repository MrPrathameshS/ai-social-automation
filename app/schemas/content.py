from pydantic import BaseModel
from typing import Optional


class ContentGenerateRequest(BaseModel):
    topic_id: int
    platform: str
    category_id: Optional[int] = None
