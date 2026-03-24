from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.conversation_v2.schemas import (
    ChatRequest,
    ChatResponse,
)

from app.conversation_v2.service import run_conversation

from app.db.session import get_db


router = APIRouter(
    prefix="/conversation_v2",
    tags=["conversation_v2"],
)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):

    result = run_conversation(
        db=db,
        user_message=request.message,
        state=request.state,
    )

    return ChatResponse(
        reply=result["reply"],
        state=result["state"],
        stage=result["stage"],
    )