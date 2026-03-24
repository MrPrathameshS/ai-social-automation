from sqlalchemy.orm import Session
from app.db.models import PromptTemplate, PromptPerformanceLog, BrandProfile
from app.services.brand_insight_learner import learn_from_prompt_failure

ROLLBACK_THRESHOLD = 0.3  # 30% drop required to rollback


def auto_rollback_if_needed(db: Session, brand_id: int, platform: str):
    print(f"🧪 [DEBUG] auto_rollback_if_needed called for brand={brand_id}, platform={platform}")

    logs = (
        db.query(PromptPerformanceLog)
        .filter(
            PromptPerformanceLog.brand_id == brand_id,
            PromptPerformanceLog.platform == platform
        )
        .order_by(PromptPerformanceLog.created_at.desc())
        .limit(2)
        .all()
    )

    print(f"🧪 [DEBUG] Found {len(logs)} performance logs for brand={brand_id}, platform={platform}")

    if len(logs) < 2:
        print("🧪 [DEBUG] Not enough logs to evaluate rollback")
        return

    latest, previous = logs[0], logs[1]
    print(f"🧪 [DEBUG] Latest score: {latest.engagement_score}, Previous score: {previous.engagement_score}")

    # Calculate drop ratio
    drop = previous.engagement_score - latest.engagement_score
    drop_ratio = drop / max(previous.engagement_score, 0.0001)

    print(f"📉 Drop ratio: {drop_ratio:.2%}")

    if drop_ratio < ROLLBACK_THRESHOLD:
        print("🧪 [DEBUG] Drop not severe enough. No rollback.")
        return

    print(f"⛔ [ROLLBACK] Triggered for brand {brand_id} on {platform}")

    bad_prompt = db.query(PromptTemplate).filter(PromptTemplate.id == latest.prompt_id).first()

    if bad_prompt:
        print(f"🧪 [DEBUG] Deactivating prompt id={bad_prompt.id}, version={bad_prompt.version}")
        bad_prompt.is_active = False   # soft delete
    else:
        print("🧪 [DEBUG] No bad_prompt found")

    brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()

    if brand:
        failure_context = f"Prompt version {bad_prompt.version if bad_prompt else 'unknown'} underperformed on {platform}."
        print("🧪 [DEBUG] Calling brand insight learner...")
        learn_from_prompt_failure(db, brand, platform, failure_context)
    else:
        print("🧪 [DEBUG] Brand not found")

    db.commit()
    print("🧪 [DEBUG] Rollback + learning committed")
