from typing import Dict, Any


def decide_story(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    yes_words = ["yes", "y", "correct", "right", "ok", "okay"]

    # If confirming refined story
    if stage == "REFINE_STORY":

        if text in yes_words:
            return {
                "action": "accept",
            }

    # If story too short → refine
    if len(user_input.split()) < 5:
        return {
            "action": "refine",
        }

    # Otherwise confirm
    return {
        "action": "confirm",
    }