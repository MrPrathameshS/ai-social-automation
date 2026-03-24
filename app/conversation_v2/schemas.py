from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    message: str
    state: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str
    state: Dict[str, Any]
    stage: str