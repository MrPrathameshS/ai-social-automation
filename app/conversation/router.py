# app/conversation/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.conversation.schemas import ChatRequest, ChatResponse
from app.conversation.conversation_service import handle_message


router = APIRouter(
    prefix="/chat",
    tags=["conversation"],
)


@router.post("/", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
):

    response = handle_message(
        db=db,
        session_id=req.session_id,
        message=req.message,
    )

    return response