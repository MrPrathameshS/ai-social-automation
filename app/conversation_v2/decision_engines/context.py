from typing import Dict, Any
from app.conversation_v2.constants.context import ALLOWED_CONTEXTS


def decide_context(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    if stage == "ASK_CONTEXT":

        if text in ALLOWED_CONTEXTS:
            return {
                "action": "accept",
                "value": text,
            }

        return {
            "action": "repeat",
        }

    return {"action": "repeat"}