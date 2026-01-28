from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import PostingStrategy
from app.services.ai_generator import client


SYSTEM_PROMPT = """
You are an expert growth strategist AI.
A previous posting strategy is underperforming.
Your job is to propose a NEW improved posting strategy based on engagement decline.
Focus on timing, platform differences, and experimentation.
Return concise actionable strategy.
"""


def mutate_strategy(old_strategy_text: str):
    print("🧬 Strategy Mutator started...")

    db: Session = SessionLocal()

    try:
        prompt = f"""
CURRENT STRATEGY:
{old_strategy_text}

This strategy is showing engagement decline.
Propose a new improved strategy with:
- New posting times
- Experimentation plan
- Platform-specific adjustments
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        new_strategy = response.choices[0].message.content.strip()

        strategy_record = PostingStrategy(strategy_text=new_strategy)
        db.add(strategy_record)
        db.commit()

        print("\n🧬 NEW STRATEGY GENERATED")
        print("----------------------------------------")
        print(new_strategy)
        print("----------------------------------------")
        print("💾 New strategy saved to database")

    except Exception as e:
        print(f"❌ Strategy mutator error: {e}")
        db.rollback()
    finally:
        db.close()
