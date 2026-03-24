from typing import Dict, Any


def decide_topic(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    yes_words = ["yes", "y", "correct", "right", "ok", "okay"]

    previous = state.get("topic")

    # ------------------------
    # CONFIRM_TOPIC
    # ------------------------

    if stage == "CONFIRM_TOPIC":

        if text in yes_words:
            return {
                "action": "accept",
            }

        # anything else → refine
        return {
            "action": "back",
            "stage": "REFINE_TOPIC",
        }

    # ------------------------
    # REFINE_TOPIC
    # ------------------------

    if stage == "REFINE_TOPIC":

        if text in yes_words:
            return {
                "action": "accept",
            }

        # short input → keep refining
        if len(user_input.split()) <= 2:
            return {
                "action": "refine",
            }

        # merge with previous topic
        if previous:
            merged = f"{previous}. {user_input}"
        else:
            merged = user_input

        return {
            "action": "confirm",
            "value": merged,
        }

    # ------------------------
    # ASK_TOPIC
    # ------------------------

    if stage == "ASK_TOPIC":

        if len(user_input.split()) <= 2:
            return {
                "action": "refine",
            }

        return {
            "action": "confirm",
            "value": user_input,
        }

    # ------------------------
    # fallback
    # ------------------------

    return {
        "action": "repeat",
    }