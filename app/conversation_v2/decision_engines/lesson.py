from typing import Dict, Any


def decide_lesson(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    # confirm stage
    if stage == "REFINE_LESSON":

        if text in ["yes", "y", "correct", "right"]:
            return {
                "action": "accept",
            }

        if text in ["no", "change", "not"]:
            return {
                "action": "refine",
            }

    # too short → refine
    if len(user_input.split()) < 3:
        return {
            "action": "refine",
        }

    # normal → confirm
    return {
        "action": "confirm",
    }