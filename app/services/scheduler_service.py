from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import GeneratedContent

from app.services.posting.linkedin_poster import post_to_linkedin_mock
from app.services.posting.instagram_poster import post_to_instagram_mock
from app.services.platform_rewriter import rewrite_for_platform


POSTER_ROUTER = {
    "linkedin": post_to_linkedin_mock,
    "instagram": post_to_instagram_mock,
}


def run_scheduler():
    print("🕒 Scheduler started...")
    db: Session = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        items = db.query(GeneratedContent).filter(
            GeneratedContent.status == "approved",
            GeneratedContent.scheduled_at != None,
            GeneratedContent.scheduled_at <= now
        ).all()

        if not items:
            print("🕒 Scheduler found 0 items to post")
            return

        print(f"📌 Scheduler found {len(items)} items to post")

        for item in items:
            platform = item.platform.lower()

            print(f"➡️ Routing content ID {item.id} to {platform}...")

            poster_fn = POSTER_ROUTER.get(platform)

            if not poster_fn:
                print(f"⚠️ No poster found for platform: {platform}")
                continue

            # 🔁 AI REWRITE LAYER (THIS IS THE UPGRADE)
            print(f"🔁 Rewriting content ID {item.id} for {platform}...")
            rewritten_text = rewrite_for_platform(item.content_text, platform)
            item.content_text = rewritten_text

            poster_fn(item)

            item.status = "posted"
            item.posted_at = datetime.utcnow()

        db.commit()
        print("✅ Scheduler posting complete")

    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        db.rollback()
    finally:
        db.close()
