# app/core/llm_models.py

import os
from groq import Groq

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_cached_model: str | None = None


def get_default_groq_model() -> str:
    """
    Dynamically select a currently supported Groq chat model.
    Cached after first successful lookup.
    """
    global _cached_model

    if _cached_model:
        return _cached_model

    models = _client.models.list().data

    # Prefer instruction / chat capable models
    preferred_keywords = ["it", "instruct", "chat"]

    for model in models:
        name = model.id.lower()
        if any(k in name for k in preferred_keywords):
            _cached_model = model.id
            return _cached_model

    # Absolute fallback: first available model
    _cached_model = models[0].id
    return _cached_model
