from typing import Dict, Any

from app.conversation_v2.constants.audience import (
    AUDIENCE_OPTIONS,
    AUDIENCE_KEYWORDS,
)


def decide_audience(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    if text in AUDIENCE_OPTIONS:
        return {
            "action": "accept",
            "value": AUDIENCE_OPTIONS[text],
        }

    for aud in AUDIENCE_OPTIONS.values():
        if aud in text:
            return {
                "action": "accept",
                "value": aud,
            }

    for aud, words in AUDIENCE_KEYWORDS.items():
        for w in words:
            if w in text:
                return {
                    "action": "accept",
                    "value": aud,
                }

    return {
        "action": "refine"
    }