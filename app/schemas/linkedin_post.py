from pydantic import BaseModel
from datetime import datetime


class LinkedInPostResponse(BaseModel):
    id: int
    linkedin_post_urn: str
    text: str
    status: str
    error_message: str | None
    published_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2

class LinkedInPostListResponse(BaseModel):
    items: list[LinkedInPostResponse]
    total: int
    limit: int
    offset: int
