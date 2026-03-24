# app/insight/service.py

from sqlalchemy.orm import Session

from app.db.models.insight import Insight
from app.db.models.conversation_state import ConversationState

from app.insight.extractor import extract_insight


def get_state(db: Session, session_id: int) -> ConversationState:

    state = (
        db.query(ConversationState)
        .filter(ConversationState.session_id == session_id)
        .first()
    )

    if not state:
        raise ValueError("Conversation state not found")

    return state


def save_insight(
    db: Session,
    session_id: int,
) -> Insight:

    # 1️⃣ load state
    state = get_state(db, session_id)

    # 2️⃣ call extractor (LLM)
    data = extract_insight(state)

    # 3️⃣ create insight row
    insight = Insight(
        session_id=session_id,
        topic=data.get("topic"),
        challenge=data.get("challenge"),
        lesson=data.get("lesson"),
        angle=data.get("angle"),
        tone=data.get("tone"),
        tags=data.get("tags"),
    )

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return insight
