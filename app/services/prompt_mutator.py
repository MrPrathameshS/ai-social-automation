from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import SessionLocal
from app.db.models import PostingStrategy
from app.services.ai_generator import client


SYSTEM_PROMPT = """
You are an expert social media growth strategist and optimizer.

Your task:
Given the current posting strategy and performance drift, generate an improved strategy.
You must adapt tone, hooks, CTA style, content structure, and emotional framing.

Return ONLY the new strategy text.
Do not explain. Do not format. Do not add headings.
"""


def mutate_posting_strategy(drift_reason: str):
    print("🧬 Prompt Mutation Engine started...")

    db: Session = SessionLocal()

    try:
        last_strategy = (
            db.query(PostingStrategy)
            .order_by(PostingStrategy.created_at.desc())
            .first()
        )

        base_strategy = last_strategy.strategy_text if last_strategy else "No prior strategy. Create a strong default strategy."

        prompt = f"""
CURRENT STRATEGY:
{base_strategy}

DRIFT REASON:
{drift_reason}

Generate a new improved posting strategy that will increase engagement and reach.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        new_strategy = response.choices[0].message.content.strip()

        db.add(PostingStrategy(
            strategy_text=new_strategy,
            created_at=datetime.utcnow()
        ))

        db.commit()

        print("🧬 New mutated strategy saved to database")
        print("--------------------------------------------------")
        print(new_strategy)
        print("--------------------------------------------------")

        return new_strategy

    except Exception as e:
        print(f"❌ Prompt mutation error: {e}")
        db.rollback()
        return None
    finally:
        db.close()
