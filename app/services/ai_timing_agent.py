from datetime import datetime, timezone
from app.services.ai_generator import client   # your existing LLM client


SYSTEM_PROMPT = """
You are a social media growth expert.
Your job is to decide the best time to post content for maximum engagement.

Rules:
- Return ONLY a datetime in ISO 8601 format
- Use UTC timezone
- Example: 2026-01-09T10:00:00Z
- Do NOT explain
"""


def get_best_post_time(platform: str, topic: str, content: str) -> datetime:
    prompt = f"""
Platform: {platform}
Topic: {topic}

Content:
{content}

Decide the best posting datetime.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # or whichever Groq model you are using
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw_time = response.choices[0].message.content.strip()

    # Parse to datetime
    dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))

    return dt.astimezone(timezone.utc)
