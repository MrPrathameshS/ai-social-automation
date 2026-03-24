from sqlalchemy.orm import Session
from app.db.models import PromptPerformanceLog, PromptTemplate, EngagementLog, GeneratedContent


def compute_engagement_score(impressions, likes, comments, shares):
    if impressions == 0:
        return 0
    return (likes * 1 + comments * 2 + shares * 3) / impressions


def score_prompt_performance(db: Session, brand_id: int, platform: str):
    print(f"🧪 [SCORER] Scoring prompt for brand={brand_id}, platform={platform}")

    latest_prompt = (
        db.query(PromptTemplate)
        .filter(
            PromptTemplate.brand_id == brand_id,
            PromptTemplate.platform == platform
        )
        .order_by(PromptTemplate.version.desc())
        .first()
    )

    if not latest_prompt:
        print("🧪 [SCORER] No latest_prompt found")
        return None

    print(f"🧪 [SCORER] Found latest_prompt id={latest_prompt.id}, version={latest_prompt.version}")

    contents = (
        db.query(GeneratedContent)
        .filter(
            GeneratedContent.brand_id == brand_id,
            GeneratedContent.platform == platform
        )
        .order_by(GeneratedContent.created_at.desc())
        .limit(5)
        .all()
    )

    print(f"🧪 [SCORER] Found {len(contents)} generated contents")

    if not contents:
        print("🧪 [SCORER] No generated content found")
        return None

    total_impressions = total_likes = total_comments = total_shares = 0

    for content in contents:
        print(f"🧪 [SCORER] Processing content id={content.id}")
        logs = db.query(EngagementLog).filter(EngagementLog.content_id == content.id).all()
        print(f"🧪 [SCORER] Found {len(logs)} engagement logs")

        for log in logs:
            total_impressions += log.impressions
            total_likes += log.likes
            total_comments += log.comments
            total_shares += log.shares

    print(
        f"🧪 [SCORER] Totals → impressions={total_impressions}, likes={total_likes}, comments={total_comments}, shares={total_shares}"
    )

    score = compute_engagement_score(
        total_impressions, total_likes, total_comments, total_shares
    )

    print(f"🧪 [SCORER] Computed engagement score = {score}")

    perf_log = PromptPerformanceLog(
        brand_id=brand_id,
        prompt_id=latest_prompt.id,
        platform=platform,
        impressions=total_impressions,
        likes=total_likes,
        comments=total_comments,
        shares=total_shares,
        engagement_score=score
    )

    db.add(perf_log)
    db.commit()

    print("🧪 [SCORER] PromptPerformanceLog inserted")

    return score
