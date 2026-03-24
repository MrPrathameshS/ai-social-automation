from typing import Dict, Any


def decide_project(
    user_input: str,
    state: Dict[str, Any],
    stage: str,
) -> Dict[str, Any]:

    text = user_input.strip()

    # ------------------------
    # ASK_PROJECT
    # save project name
    # ------------------------

    if stage == "ASK_PROJECT":

        if len(text) < 2:
            return {"action": "refine"}

        return {
            "action": "accept",
            "value": user_input,
        }

    # ------------------------
    # ASK_PROJECT_DESC
    # save description
    # ------------------------

    if stage == "ASK_PROJECT_DESC":

        if len(text) < 2:
            return {"action": "repeat"}

        return {
            "action": "accept",
            "value": user_input,
        }

    return {"action": "repeat"}