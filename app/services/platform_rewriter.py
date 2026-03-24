from app.services.ai_generator import generate_content


def rewrite_for_platform(base_text: str, platform: str) -> str:
    if platform == "linkedin":
        prompt = f"""
Rewrite the following content for LinkedIn.

Tone: professional, insightful, leadership-focused.
Style: short paragraphs, optional bullet points, no emojis.

Content:
{base_text}
"""

    elif platform == "instagram":
        prompt = f"""
Rewrite the following content for Instagram.

Tone: energetic, inspirational, modern.
Format rules:
- Start with a strong hook
- Use short lines
- Use 1–3 relevant emojis
- End with 3–5 relevant hashtags

Content:
{base_text}
"""

    else:
        return base_text  # fallback

    rewritten = generate_content(prompt=prompt)
    return rewritten
