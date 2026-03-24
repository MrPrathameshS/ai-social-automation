from typing import Dict, Any


INTENT_OPTIONS = {
    "1": "teach",
    "2": "build_authority",
    "3": "attract_recruiters",
    "4": "promote_project",
    "5": "share_progress",
    "6": "tell_story",
}


KEYWORDS = {
    "teach": ["teach", "explain", "share lesson", "educate"],
    "build_authority": ["authority", "credibility", "expert", "show expertise"],
    "attract_recruiters": ["recruiter", "job", "hiring", "opportunity"],
    "promote_project": ["promote", "launch", "project", "product", "saas"],
    "share_progress": ["progress", "update", "journey", "building"],
    "tell_story": ["story", "experience", "what happened"],
}


def decide_intent(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.lower().strip()

    # ------------------------
    # number choice
    # ------------------------

    if text in INTENT_OPTIONS:
        return {
            "action": "accept",
            "value": INTENT_OPTIONS[text],
        }

    # ------------------------
    # direct match
    # ------------------------

    for key in INTENT_OPTIONS.values():
        if key in text:
            return {
                "action": "accept",
                "value": key,
            }

    # ------------------------
    # keyword match
    # ------------------------

    for intent, words in KEYWORDS.items():
        for w in words:
            if w in text:
                return {
                    "action": "accept",
                    "value": intent,
                }

    # ------------------------
    # not clear → refine
    # ------------------------

    return {
        "action": "refine"
    }