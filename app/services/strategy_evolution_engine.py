from app.services.strategy_drift_detector import detect_strategy_drift
from app.services.strategy_mutator import mutate_strategy
from app.db.session import SessionLocal
from app.db.models import PostingStrategy


def run_strategy_evolution():
    print("🧠 Strategy Evolution Engine started...")

    drift = detect_strategy_drift()

    if not drift:
        print("🧠 Strategy stable. No mutation required.")
        return

    db = SessionLocal()
    try:
        last_strategy = (
            db.query(PostingStrategy)
            .order_by(PostingStrategy.created_at.desc())
            .first()
        )

        old_text = last_strategy.strategy_text if last_strategy else "No prior strategy."

    finally:
        db.close()

    mutate_strategy(old_text)
