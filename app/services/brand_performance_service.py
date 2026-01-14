from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import BrandProfile, GeneratedContent, EngagementLog


def get_brand_performance_summary(db: Session, brand_id: int) -> dict:
    results = (
        db.query(
            func.avg(EngagementLog.likes).label("avg_likes"),
            func.avg(EngagementLog.comments).label("avg_comments"),
            func.avg(EngagementLog.shares).label("avg_shares"),
            func.count(EngagementLog.id).label("count")
        )
        .join(GeneratedContent, EngagementLog.content_id == GeneratedContent.id)
        .filter(GeneratedContent.brand_id == brand_id)
        .first()
    )

    # You can extend with historical comparisons
    return {
        "avg_likes": results.avg_likes or 0,
        "avg_comments": results.avg_comments or 0,
        "avg_shares": results.avg_shares or 0,
        "count": results.count or 0,
        "engagement_drop_percent": 30,  # placeholder – compute via history
        "consecutive_failures": 2       # placeholder – compute via prompt logs
    }
