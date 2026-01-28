from sqlalchemy.orm import Session
from collections import defaultdict
from app.db.session import SessionLocal
from app.db.models import EngagementLog, PostingStrategy
from app.services.ai_generator import client


SYSTEM_PROMPT = """
You are an expert social media growth strategist.
Analyze performance data and derive optimal posting strategies.
Focus on time patterns, platform differences, and engagement quality.
Return concise, actionable insights.
"""


def analyze_performance_and_learn():
    print("🧠 AI Performance Analyzer started...")
    db: Session = SessionLocal()

    try:
        logs = db.query(EngagementLog).all()

        if not logs:
            print("🕒 No engagement data available for analysis")
            return

        # Aggregate stats
        stats = defaultdict(list)

        for log in logs:
            stats[log.platform].append({
                "likes": log.likes,
                "comments": log.comments,
                "shares": log.shares,
                "impressions": log.impressions,
                "time": log.recorded_at.strftime("%A %H:%M")
            })

        prompt = "Here is engagement performance data grouped by platform:\n\n"

        for platform, entries in stats.items():
            prompt += f"\nPlatform: {platform}\n"
            for e in entries:
                prompt += (
                    f"- {e['time']} | Likes: {e['likes']}, "
                    f"Comments: {e['comments']}, Shares: {e['shares']}, "
                    f"Impressions: {e['impressions']}\n"
                )

        prompt += "\nBased on this data, identify optimal posting times and strategy adjustments."

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        insight = response.choices[0].message.content

        # 🔥 SAVE STRATEGY TO DB (CRITICAL STEP)
        strategy = PostingStrategy(
            platform="all",
            strategy_text=insight
        )

        db.add(strategy)
        db.commit()

        print("\n📊 AI PERFORMANCE INSIGHTS")
        print("--------------------------------------------------")
        print(insight)
        print("--------------------------------------------------\n")
        print("💾 Strategy saved to database")
        print("✅ AI performance analysis complete")

    except Exception as e:
        print(f"❌ AI performance analyzer error: {e}")
        db.rollback()
    finally:
        db.close()
