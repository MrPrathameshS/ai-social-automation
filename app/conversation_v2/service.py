from typing import Dict, Any

from app.conversation_v2.state_manager import (
    create_empty_state,
    get_stage,
    set_stage,
    update_field,
)

from app.conversation_v2.planner import plan

from app.conversation_v2.question_generator import generate_question

from app.conversation_v2.summary_builder import build_summary

# ✅ NEW
from app.services.conversation_content_service import (
    generate_content_item_from_plan
)


def run_conversation(
        db,
        user_message: str,
        state: Dict[str, Any] | None,
    ):

    # -------------------------
    # 1. first call → create state
    # -------------------------
    if not state:
        state = create_empty_state()

        stage = get_stage(state)

        reply = generate_question(
            stage=stage,
            state=state,
            user_input="",
        )

        state["last_user_message"] = ""
        state["last_assistant_message"] = reply

        return {
            "reply": reply,
            "state": state,
            "stage": stage,
        }

    # -------------------------
    # 2. get current stage
    # -------------------------
    current_stage = get_stage(state)

    # -------------------------
    # SUMMARY handling
    # -------------------------
    if current_stage == "SUMMARY":

        msg = user_message.strip()

        # -------------------------
        # GENERATE
        # -------------------------
        if msg.lower() == "generate":

            brand_id = 1  # TODO get from user session

            item = generate_content_item_from_plan(
                db=db,
                brand_id=brand_id,
                plan=state,
            )

            # ✅ store content id for next pipeline steps
            state["content_item_id"] = item.id

            set_stage(state, "GENERATE")

            reply = f"Post generated. ContentItem id={item.id}"

            state["last_user_message"] = user_message
            state["last_assistant_message"] = reply

            return {
                "reply": reply,
                "state": state,
                "stage": "DONE",
                "content_item_id": item.id,
            }

        # -------------------------
        # INLINE EDIT
        # -------------------------
        field_map = {
            "topic": "topic",
            "project": "project",
            "context": "context",
            "story": "story",
            "lesson": "lesson",
            "angle": "angle",
            "intent": "intent",
            "tone": "tone",
            "audience": "audience",
        }

        if ":" in msg:

            key, value = msg.split(":", 1)

            key = key.strip().lower()
            value = value.strip()

            if key in field_map:
                state[field_map[key]] = value

        reply = build_summary(state)

        state["last_user_message"] = user_message
        state["last_assistant_message"] = reply

        return {
            "reply": reply,
            "state": state,
            "stage": "SUMMARY",
        }

    # -------------------------
    # 3. planner
    # -------------------------
    result = plan(
        current_stage=current_stage,
        user_input=user_message,
        state=state,
    )

    next_stage = result["next_stage"]
    updates = result["updates"]

    # -------------------------
    # 4. update state
    # -------------------------
    if updates:
        update_field(state, updates)

    # -------------------------
    # 5. set stage
    # -------------------------
    set_stage(state, next_stage)

    # -------------------------
    # 6. generate reply
    # -------------------------
    if next_stage == "SUMMARY":

        reply = build_summary(state)

    else:

        reply = generate_question(
            stage=next_stage,
            state=state,
            user_input=user_message,
        )

    # -------------------------
    # 7. store messages
    # -------------------------
    state["last_user_message"] = user_message
    state["last_assistant_message"] = reply

    # -------------------------
    # 8. return
    # -------------------------
    return {
        "reply": reply,
        "state": state,
        "stage": next_stage,
    }