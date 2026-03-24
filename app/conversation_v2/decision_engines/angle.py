from typing import Dict, Any


def decide_angle(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.strip()

    # empty input → ask again
    if not text:
        return {
            "action": "retry",
        }

    # accept anything
    return {
        "action": "accept",
    }