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

    # Prefer instruction/chat-style models
    preferred_keywords = ["it", "instruct", "chat"]

    for model in models:
        name = model.id.lower()
        if any(k in name for k in preferred_keywords):
            _cached_model = model.id
            return _cached_model

    # Absolute fallback
    _cached_model = models[0].id
    return _cached_model


class LLMClient:
    def __init__(self):
        self.client = _client

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=get_default_groq_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content


_llm_client = LLMClient()


def call_llm(prompt: str, system_prompt: str = "You are a helpful AI assistant.") -> str:
    return _llm_client.chat(system_prompt=system_prompt, user_prompt=prompt)
