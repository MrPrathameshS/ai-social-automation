from typing import Dict, Any

from app.conversation_v2.stage_config import STAGES, STAGE_CONFIG

from app.conversation_v2.decision_engines import (
    decide_topic,
    decide_story,
    decide_lesson,
    decide_angle,
)

from app.conversation_v2.decision_engines.intent import decide_intent
from app.conversation_v2.decision_engines.tone import decide_tone
from app.conversation_v2.decision_engines.audience import decide_audience
from app.conversation_v2.decision_engines.project import decide_project
from app.conversation_v2.decision_engines.context import decide_context
# ------------------------
# stage helpers
# ------------------------

def get_next_stage(current_stage: str) -> str:

    if current_stage not in STAGES:
        return STAGES[0]

    idx = STAGES.index(current_stage)

    if idx + 1 >= len(STAGES):
        return "DONE"

    return STAGES[idx + 1]


def get_stage_config(stage: str) -> Dict[str, Any]:
    return STAGE_CONFIG.get(stage, {})


# ------------------------
# decision routing
# ------------------------

def run_decision_engine(
    stage: str,
    user_input: str,
    state: Dict[str, Any],
) -> Dict[str, Any] | None:

    stage = stage.upper()

    if stage.startswith("ASK_TOPIC") or stage.startswith("REFINE_TOPIC") or stage.startswith("CONFIRM_TOPIC"):
        return decide_topic(user_input, state, stage)
    if stage.startswith("ASK_PROJECT"):
        return decide_project(user_input, state, stage)
    if stage.startswith("ASK_CONTEXT"):
        return decide_context(user_input, state, stage)
    if stage.startswith("ASK_STORY") or stage.startswith("REFINE_STORY"):
        return decide_story(user_input, state, stage)

    if stage.startswith("ASK_LESSON") or stage.startswith("REFINE_LESSON"):
        return decide_lesson(user_input, state, stage)

    if stage.startswith("ASK_ANGLE") or stage.startswith("REFINE_ANGLE"):
        return decide_angle(user_input, state, stage)

    if stage.startswith("ASK_INTENT"):
        return decide_intent(user_input, state, stage)

    if stage.startswith("ASK_TONE"):
        return decide_tone(user_input, state, stage)

    if stage.startswith("ASK_AUDIENCE"):
        return decide_audience(user_input, state, stage)

    return None


# ------------------------
# planner
# ------------------------

def plan(
    current_stage: str,
    user_input: str,
    state: Dict[str, Any],
) -> Dict[str, Any]:

    config = get_stage_config(current_stage)

    field = config.get("field")

    updates: Dict[str, Any] = {}

    decision = run_decision_engine(
        current_stage,
        user_input,
        state,
    )

    # ------------------------
    # SAVE FIELD ALWAYS
    # ------------------------

    if field:

        if decision and "value" in decision:
            updates[field] = decision["value"]

        else:
            updates[field] = user_input

    # ------------------------
    # decision handling
    # ------------------------

    if decision:

        action = decision["action"]

        if action == "back":
            return {
                "next_stage": decision["stage"],
                "updates": updates,
            }

        if action in ["refine", "confirm", "accept"]:

            next_stage = get_next_stage(current_stage)

            return {
                "next_stage": next_stage,
                "updates": updates,
            }

    # ------------------------
    # default behavior
    # ------------------------

    next_stage = get_next_stage(current_stage)

    return {
        "next_stage": next_stage,
        "updates": updates,
    }