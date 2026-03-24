from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import PromptTemplate
from app.services.ai_generator import client


MUTATION_RULES = {
    "hook": "Improve the opening hook to be more attention-grabbing and emotionally compelling.",
    "cta": "Improve the call-to-action to drive comments, shares, or reflection.",
    "tone": "Adjust the tone to be more authoritative, confident, and insightful.",
    "format": "Change the structure or format to improve readability and engagement (e.g. story, bullet points, questions).",
    "emotion": "Inject stronger emotional appeal such as aspiration, urgency, or curiosity."
}


SYSTEM_PROMPT = """
You are an expert social media copy strategist.
Your job is to improve prompts used to generate high-performing social content.
You must respect the platform style and brand tone.
You only output the improved prompt text. No explanations.
"""


def mutate_prompts(platform: str, performance_summary: str):
    print(f"🧬 Prompt Mutation Engine triggered for {platform}")

    db: Session = SessionLocal()

    try:
        # 1. Fetch latest prompt
        base_prompt_record = (
            db.query(PromptTemplate)
            .filter(PromptTemplate.platform == platform)
            .order_by(PromptTemplate.created_at.desc())
            .first()
        )

        if not base_prompt_record:
            print(f"⚠️ No base prompt found for {platform}, skipping mutation.")
            return

        base_prompt = base_prompt_record.prompt_text

        # 2. Decide mutation types (rule-driven)
        mutations_to_apply = ["hook", "cta", "emotion"]

        print(f"🔁 Applying mutations: {mutations_to_apply}")

        mutation_instructions = "\n".join(
            f"- {MUTATION_RULES[m]}" for m in mutations_to_apply
        )

        user_prompt = f"""
CURRENT PROMPT:
{base_prompt}

PERFORMANCE ISSUE:
{performance_summary}

MUTATION INSTRUCTIONS:
{mutation_instructions}

Return the improved full prompt text for {platform}.
"""

        # 3. LLM call to mutate prompt
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
        )

        mutated_prompt = response.choices[0].message.content.strip()

        # 4. Save new prompt version
        new_prompt = PromptTemplate(
            platform=platform,
            prompt_text=mutated_prompt,
            mutation_reason=performance_summary
        )

        db.add(new_prompt)
        db.commit()

        print(f"✅ Prompt mutated and saved for {platform}")

    except Exception as e:
        db.rollback()
        print(f"❌ Prompt mutation error: {e}")

    finally:
        db.close()
