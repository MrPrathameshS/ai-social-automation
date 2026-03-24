from typing import Dict, List

STAGES: List[str] = [

    "ASK_TOPIC",
    "REFINE_TOPIC",
    "CONFIRM_TOPIC",

    "ASK_PROJECT",
    "ASK_PROJECT_DESC",

    "ASK_CONTEXT",

    "ASK_STORY",
    "REFINE_STORY",

    "ASK_LESSON",
    "REFINE_LESSON",

    "ASK_ANGLE",

    "ASK_INTENT",
    "ASK_TONE",
    "ASK_AUDIENCE",

    "SUMMARY",
    "EDIT",
    "GENERATE",
    "DONE",
]


STAGE_CONFIG: Dict[str, Dict] = {

    "ASK_TOPIC": {
        "field": "topic",
        "confirm": False,
        "refine": True,
        "rag": False,
    },

    "REFINE_TOPIC": {
        "field": "topic",
        "confirm": True,
        "refine": True,
        "rag": False,
    },

    "CONFIRM_TOPIC": {
        "field": "topic",
        "confirm": True,
        "refine": False,
        "rag": False,
        "options": ["yes", "refine"],
    },

    "ASK_PROJECT": {
        "field": "project",
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "ASK_PROJECT_DESC": {
        "field": "project_desc",
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "ASK_CONTEXT": {
        "field": "context",
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "ASK_STORY": {
        "field": "story",
        "confirm": False,
        "refine": True,
        "rag": True,
    },

    "REFINE_STORY": {
        "field": "story",
        "confirm": True,
        "refine": True,
        "rag": True,
    },

    "ASK_LESSON": {
        "field": "lesson",
        "confirm": False,
        "refine": True,
        "rag": True,
    },

    "REFINE_LESSON": {
        "field": "lesson",
        "confirm": True,
        "refine": True,
        "rag": True,
    },

    # ✅ no refine for angle anymore
    "ASK_ANGLE": {
        "field": "angle",
        "confirm": False,
        "refine": False,
        "rag": True,
    },

    "ASK_INTENT": {
        "field": "intent",
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "ASK_TONE": {
        "field": "tone",
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "ASK_AUDIENCE": {
        "field": "audience",
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "SUMMARY": {
        "field": None,
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "EDIT": {
        "field": None,
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "GENERATE": {
        "field": None,
        "confirm": False,
        "refine": False,
        "rag": False,
    },

    "DONE": {
        "field": None,
        "confirm": False,
        "refine": False,
        "rag": False,
    },
}