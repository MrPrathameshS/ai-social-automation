from sqlalchemy.orm import Session
from app.db.models import BrandProfile
from app.core.llm import call_llm


def learn_from_prompt_failure(db: Session, brand: BrandProfile, platform: str, failure_context: str):
    """
    Analyze prompt failure and update brand learned_insights.
    """

    system_prompt = "You are an expert brand strategist and growth analyst."

    user_prompt = f"""
Brand Name: {brand.brand_name}

Platform: {platform}

Current Brand Personality:
Tone: {brand.tone_description}
Audience: {brand.audience_description}
Writing Style: {brand.writing_style}
Constraints: {brand.do_not_use}

Failure Context:
{failure_context}

Task:
1. Identify why the content likely underperformed.
2. Suggest adjustments to tone, style, or messaging.
3. Produce 1-2 concise insights to store as brand memory.
"""

    insights = call_llm(user_prompt, system_prompt)

    brand.learned_insights = (brand.learned_insights or "") + f"\n{insights}"

    db.commit()

    print(f"🧠 Brand insight updated for {brand.brand_name}")
