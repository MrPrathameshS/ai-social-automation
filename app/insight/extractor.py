# app/insight/extractor.py

import json

from app.core.llm import call_llm
from app.db.models.conversation_state import ConversationState


def build_prompt(state: ConversationState) -> str:

    return f"""
We finished a conversation for building a LinkedIn post.

Conversation data:

topic: {state.topic}
challenge: {state.challenge}
lesson: {state.lesson}
angle: {state.angle}

Extract structured insight.

Return JSON only.

Format:

{{
  "topic": "...",
  "challenge": "...",
  "lesson": "...",
  "angle": "...",
  "tone": "...",
  "tags": "comma separated"
}}
"""


def build_system_prompt():

    return """
You extract structured insight.

Return valid JSON only.

Do not explain.
Do not add text.
Only JSON.
"""


def call_extractor_llm(prompt: str) -> dict:

    text = call_llm(
        prompt=prompt,
        system_prompt=build_system_prompt()
    )

    try:
        return json.loads(text)

    except Exception:

        start = text.find("{")
        end = text.rfind("}") + 1

        return json.loads(text[start:end])


def extract_insight(state: ConversationState) -> dict:

    prompt = build_prompt(state)

    result = call_extractor_llm(prompt)

    return result