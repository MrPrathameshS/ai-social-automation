# app/rag/retriever.py

from app.rag.knowledge_data import KNOWLEDGE


def normalize_topic(topic: str | None) -> str | None:
    if not topic:
        return None

    topic = topic.lower().strip()

    for key in KNOWLEDGE.keys():
        if key in topic:
            return key

    return None


def get_knowledge(topic: str | None) -> dict:

    key = normalize_topic(topic)

    if not key:
        return {}

    return KNOWLEDGE.get(key, {})


def get_challenges(topic: str | None) -> list[str]:

    data = get_knowledge(topic)

    return data.get("challenges", [])


def get_lessons(topic: str | None) -> list[str]:

    data = get_knowledge(topic)

    return data.get("lessons", [])


def get_angles(topic: str | None) -> list[str]:

    data = get_knowledge(topic)

    return data.get("angles", [])