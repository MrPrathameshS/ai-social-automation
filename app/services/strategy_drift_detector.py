from sqlalchemy.orm import Session
from statistics import mean
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.db.models import EngagementLog, PostingStrategy, GeneratedContent, BrandProfile
from app.services.prompt_mutation_engine import mutate_prompts
from app.services.brand_mutation_engine import BrandMutationEngine

DRIFT_THRESHOLD = 0.25              # 25% performance drop
MIN_LOGS_REQUIRED = 10              # Minimum data points to evaluate
COOLDOWN_PERIOD = timedelta(days=1) # Minimum time between strategy mutations


def detect_strategy_drift():
    print("📉 Drift Detector started...")
    db: Session = SessionLocal()

    try:
        logs = (
            db.query(EngagementLog)
            .order_by(EngagementLog.recorded_at.desc())
            .all()
        )

        if len(logs) < MIN_LOGS_REQUIRED:
            print("🕒 Not enough data to detect drift")
            return False

        # Cooldown guard (strategy-level)
        last_strategy = (
            db.query(PostingStrategy)
            .order_by(PostingStrategy.created_at.desc())
            .first()
        )

        if last_strategy:
            time_since_last_strategy = datetime.utcnow() - last_strategy.created_at
            if time_since_last_strategy < COOLDOWN_PERIOD:
                print("⏳ Strategy recently updated. Skipping drift detection.")
                return False

        recent = logs[:5]
        historical = logs[5:15]

        recent_avg = mean([l.impressions for l in recent])
        historical_avg = mean([l.impressions for l in historical])

        if historical_avg == 0:
            print("⚠️ Historical average is zero. Skipping drift calculation.")
            return False

        drop_ratio = (historical_avg - recent_avg) / historical_avg

        print(
            f"📊 Recent avg: {recent_avg:.2f}, "
            f"Historical avg: {historical_avg:.2f}, "
            f"Drop: {drop_ratio:.2%}"
        )

        if drop_ratio > DRIFT_THRESHOLD:
            print("⚠️ Strategy drift detected! Triggering mutations...")

            performance_summary = {
                "historical_avg_impressions": historical_avg,
                "recent_avg_impressions": recent_avg,
                "drop_ratio": drop_ratio,
                "analysis": "Engagement performance has declined. Audience response is weakening."
            }

            # 🔥 PLATFORM PROMPT MUTATION (still valid)
            mutate_prompts("linkedin", performance_summary)
            mutate_prompts("instagram", performance_summary)

            # 🔥 BRAND MUTATION (CORRECT, DATA-DRIVEN)
            _trigger_brand_mutation(db)

            return True

        print("✅ No strategy drift detected")
        return False

    except Exception as e:
        print(f"❌ Drift detector error: {e}")
        return False

    finally:
        db.close()

def _trigger_brand_mutation(db: Session):
    print("🧠 Triggering brand mutation engine...")

    # Get recent content to identify affected brands
    recent_contents = (
        db.query(GeneratedContent)
        .order_by(GeneratedContent.created_at.desc())
        .limit(10)
        .all()
    )

    brand_ids = set()
    for content in recent_contents:
        if content.brand_id:
            brand_ids.add(content.brand_id)

    if not brand_ids:
        print("⚠️ No brand IDs found in recent content. Skipping brand mutation.")
        return

    engine = BrandMutationEngine(db)

    for brand_id in brand_ids:
        brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
        if not brand:
            continue

        print(f"🧬 Evaluating brand mutation for: {brand.brand_name}")
        engine.evaluate_and_mutate(brand_id)
