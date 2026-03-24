# app/conversation/state_manager.py

from sqlalchemy.orm import Session

from app.db.models.conversation_state import ConversationState
from app.db.models.conversation_session import ConversationSession

DEFAULT_STEP = "ASK_TOPIC"


def get_state(db: Session, session_id: int) -> ConversationState | None:
    return (
        db.query(ConversationState)
        .filter(ConversationState.session_id == session_id)
        .first()
    )


def create_state(db: Session, session_id: int) -> ConversationState:
    state = ConversationState(
        session_id=session_id,
        step=DEFAULT_STEP,
    )

    db.add(state)
    db.commit()
    db.refresh(state)

    return state


def get_or_create_state(db: Session, session_id: int):

    # ensure session exists
    get_or_create_session(db, session_id)

    state = get_state(db, session_id)

    if state is None:
        state = create_state(db, session_id)

    return state


def update_field(
    db: Session,
    state: ConversationState,
    field: str,
    value: str,
):
    setattr(state, field, value)

    db.commit()
    db.refresh(state)

    return state


def set_step(
    db: Session,
    state: ConversationState,
    step: str,
):
    state.step = step

    db.commit()
    db.refresh(state)

    return state

def get_or_create_session(db: Session, session_id: int):

    session = (
        db.query(ConversationSession)
        .filter(ConversationSession.id == session_id)
        .first()
    )

    if session is None:
        session = ConversationSession(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    return session