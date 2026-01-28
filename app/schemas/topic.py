from pydantic import BaseModel
from datetime import datetime


class TopicCreate(BaseModel):
    topic_text: str


class TopicResponse(BaseModel):
    id: int
    topic_text: str
    source: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
