from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import GeneratedContent, PostingStrategy
from app.services.ai_generator import client


SYSTEM_PROMPT = """
You are an expert social media scheduler AI.
You decide optimal posting times based on learned strategy and content context.
Always return a datetime in UTC in format: YYYY-MM-DD HH:MM
"""


def run_ai_scheduler():
    print("🧠 LLM AI Scheduler started...")
    db: Session = SessionLocal()

    try:
        # 1. Get latest learned strategy
        strategy = (
            db.query(PostingStrategy)
            .order_by(PostingStrategy.created_at.desc())
            .first()
        )

        strategy_text = strategy.strategy_text if strategy else "No prior strategy available."

        # 2. Get unscheduled approved content
        items = db.query(GeneratedContent).filter(
            GeneratedContent.status == "approved",
            GeneratedContent.scheduled_at == None
        ).all()

        if not items:
            print("🧠 No unscheduled approved content found")
            return

        now = datetime.now(timezone.utc)

        for item in items:
            print(f"🧠 Asking AI for best time for content ID {item.id} ({item.platform})")

            prompt = f"""
CONTENT:
Platform: {item.platform}
Content: {item.content_text}

LEARNED STRATEGY:
{strategy_text}

Based on the learned strategy and content, decide the best UTC datetime to post.
Return only the datetime in format: YYYY-MM-DD HH:MM
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            ai_time_str = response.choices[0].message.content.strip()

            scheduled_time = datetime.strptime(
                ai_time_str, "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc)

            # 🔒 HARD SAFETY: Never allow past scheduling
            if scheduled_time <= now:
                print(f"⚠️ AI returned past time {scheduled_time}, shifting to next week")
                scheduled_time = scheduled_time + timedelta(days=7)

            item.scheduled_at = scheduled_time

            print(f"📅 AI scheduled content ID {item.id} at {scheduled_time}")

        db.commit()
        print("✅ LLM AI scheduling complete")

    except Exception as e:
        print(f"❌ LLM AI Scheduler error: {e}")
        db.rollback()
    finally:
        db.close()
