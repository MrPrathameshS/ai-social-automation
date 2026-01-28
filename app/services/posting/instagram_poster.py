from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import GeneratedContent


def post_to_instagram_mock(content: GeneratedContent):
    print("\n================= 📸 INSTAGRAM POST =================")
    print(content.content_text)
    print("=====================================================\n")


def run_instagram_poster():
    db: Session = SessionLocal()
    try:
        items = db.query(GeneratedContent).filter(
            GeneratedContent.status == "approved",
            GeneratedContent.platform == "instagram",
            GeneratedContent.scheduled_at != None
        ).all()

        if not items:
            print("🕒 No approved content scheduled for Instagram")
            return

        for item in items:
            post_to_instagram_mock(item)
            item.status = "posted"
            item.posted_at = datetime.utcnow()

        db.commit()
        print(f"✅ Posted {len(items)} items to Instagram (mock)")

    except Exception as e:
        print(f"❌ Instagram poster error: {e}")
        db.rollback()
    finally:
        db.close()
