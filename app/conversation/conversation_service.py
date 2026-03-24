# app/conversation/conversation_service.py

from sqlalchemy.orm import Session

from app.conversation.state_manager import (
    get_or_create_state,
    update_field,
    set_step,
)

from app.conversation.planner import plan

from app.conversation.schemas import ChatResponse

from app.conversation.question_generator import generate_question

from app.insight.service import save_insight
from app.services.preview_generation_service import generate_preview_from_insight

import traceback


def handle_message(
    db: Session,
    session_id: int,
    message: str,
) -> ChatResponse:

    state = get_or_create_state(db, session_id)

    result = plan(state, message)

    field = result.get("field")
    value = result.get("value")
    next_step = result.get("next_step")

    question_type = result.get("question_type")

    reply = result.get("reply")

    done = result.get("done", False)

    # -------------------------
    # update state
    # -------------------------

    if field and value:
        state = update_field(
            db=db,
            state=state,
            field=field,
            value=value,
        )

    if next_step:
        state = set_step(
            db=db,
            state=state,
            step=next_step,
        )

    # -------------------------
    # dynamic question generation
    # -------------------------

    if question_type:

        try:
            reply = generate_question(
                state=state,
                question_type=question_type,
                user_message=message,   # IMPORTANT
            )

        except Exception:
            traceback.print_exc()
            reply = "Can you tell me more?"

    # ---------- safety fallback ----------
    if not reply:
        reply = "Okay, tell me more."

    # -------------------------
    # preview generation
    # -------------------------

    preview_text = None

    print("DONE FLAG:", done)
    print("STATE STEP:", state.step)

    if done and state.step == "DONE":

        try:

            save_insight(
                db=db,
                session_id=session_id,
            )

            preview = generate_preview_from_insight(
                db=db,
                session_id=session_id,
            )

            preview_text = preview.get("text")

            print("Insight saved + preview generated")

        except Exception:
            traceback.print_exc()

    # -------------------------
    # response
    # -------------------------

    return ChatResponse(
        reply=reply,
        step=state.step,
        done=done,
        preview=preview_text,
    )