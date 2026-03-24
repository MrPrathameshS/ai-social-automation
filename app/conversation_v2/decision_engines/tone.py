from typing import Dict, Any

from app.conversation_v2.constants.tone import (
    TONE_OPTIONS,
    TONE_KEYWORDS,
)


def decide_tone(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    # number choice

    if text in TONE_OPTIONS:
        return {
            "action": "accept",
            "value": TONE_OPTIONS[text],
        }

    # direct match

    for tone in TONE_OPTIONS.values():
        if tone in text:
            return {
                "action": "accept",
                "value": tone,
            }

    # keyword match

    for tone, words in TONE_KEYWORDS.items():
        for w in words:
            if w in text:
                return {
                    "action": "accept",
                    "value": tone,
                }

    return {
        "action": "refine"
    }