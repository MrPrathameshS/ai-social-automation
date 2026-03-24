# app/conversation/schemas.py

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: int
    message: str


from typing import Optional

class ChatResponse(BaseModel):
    reply: str
    step: str
    done: bool
    preview: Optional[str] = None