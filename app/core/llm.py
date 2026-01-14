import os
from groq import Groq


class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
