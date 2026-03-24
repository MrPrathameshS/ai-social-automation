from typing import Dict, Any


def create_empty_state():

    return {
        "stage": "ASK_TOPIC",

        "topic": None,
        "project": None,
        "context": None,
        "story": None,
        "lesson": None,
        "angle": None,
        "goal": None,
        "intent": None,
        "tone": None,
        "audience": None,
        "cta": None,

        # NEW
        "last_user_message": None,
        "last_assistant_message": None,
    }


def get_stage(state: Dict[str, Any]) -> str:
    return state.get("stage", "ASK_TOPIC")


def set_stage(state: Dict[str, Any], stage: str) -> None:
    state["stage"] = stage


def update_field(
    state: Dict[str, Any],
    updates: Dict[str, Any],
) -> None:

    for key, value in updates.items():
        state[key] = value


def get_state_value(
    state: Dict[str, Any],
    field: str,
):
    return state.get(field)