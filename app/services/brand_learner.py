from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import EngagementLog, GeneratedContent, BrandProfile
from collections import defaultdict


def learn_brand_patterns():
    print("🧬 Brand Learner started...")
    db: Session = SessionLocal()

    try:
        logs = db.query(EngagementLog).all()
        if not logs:
            print("🕒 No engagement data to learn from")
            return

        brand_scores = defaultdict(list)

        for log in logs:
            content = db.query(GeneratedContent).filter(
                GeneratedContent.id == log.content_id
            ).first()

            if not content:
                continue

            brand_scores[content.brand].append({
                "likes": log.likes,
                "comments": log.comments,
                "shares": log.shares,
                "impressions": log.impressions
            })

        for brand, metrics in brand_scores.items():
            avg_likes = sum(m["likes"] for m in metrics) / len(metrics)
            avg_comments = sum(m["comments"] for m in metrics) / len(metrics)

            insight = f"""
High performing patterns:
- Average Likes: {avg_likes:.1f}
- Average Comments: {avg_comments:.1f}
- Style preference: Posts that trigger discussion perform best
- Emotional resonance increases engagement
"""

            profile = db.query(BrandProfile).filter(
                BrandProfile.brand_name.ilike(brand)
            ).first()

            if profile:
                profile.learned_insights = insight.strip()
                print(f"🧠 Updated learned insights for brand: {brand}")

        db.commit()
        print("✅ Brand learning complete")

    except Exception as e:
        print(f"❌ Brand learner error: {e}")
        db.rollback()
    finally:
        db.close()
