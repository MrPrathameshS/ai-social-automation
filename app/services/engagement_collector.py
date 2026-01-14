import random
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import SessionLocal
from app.db.models import GeneratedContent, EngagementLog


def collect_engagement_metrics():
    print("📊 Engagement Collector started...")
    db: Session = SessionLocal()

    try:
        # Get recently posted content
        items = db.query(GeneratedContent).filter(
            GeneratedContent.status == "posted"
        ).all()

        if not items:
            print("🕒 No posted content found to collect engagement")
            return

        for item in items:
            # Simulate engagement
            likes = random.randint(10, 200)
            comments = random.randint(0, 50)
            shares = random.randint(0, 30)
            impressions = random.randint(200, 2000)

            log = EngagementLog(
                content_id=item.id,
                platform=item.platform,
                likes=likes,
                comments=comments,
                shares=shares,
                impressions=impressions,
                recorded_at=datetime.utcnow()
            )

            db.add(log)

            print(
                f"📈 Collected engagement for content {item.id} | "
                f"Likes: {likes}, Comments: {comments}, Shares: {shares}, Impressions: {impressions}"
            )

        db.commit()
        print("✅ Engagement collection complete")

    except Exception as e:
        print(f"❌ Engagement collector error: {e}")
        db.rollback()
    finally:
        db.close()
