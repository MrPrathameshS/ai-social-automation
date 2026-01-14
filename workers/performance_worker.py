from app.db.session import SessionLocal
from app.db.models import BrandProfile
from app.services.prompt_performance_scorer import score_prompt_performance
from app.services.prompt_rollback_engine import auto_rollback_if_needed
from app.services.brand_mutation_engine import BrandMutationEngine   # 🔥 NEW


def run_performance_worker():
    print("🧠 Performance Worker started...")

    db = SessionLocal()
    try:
        brands = db.query(BrandProfile).all()
        print(f"🧪 [DEBUG] Found {len(brands)} brands")

        for brand in brands:
            print(f"\n🔍 Evaluating performance for brand: {brand.brand_name} (id={brand.id})")

            for platform in ["instagram", "linkedin"]:
                print(f"   → Scoring prompt performance on {platform}")

                score = score_prompt_performance(db, brand.id, platform)
                print(f"🧪 [DEBUG] score_prompt_performance returned: {score}")

                print("🧪 [DEBUG] Calling auto_rollback_if_needed...")
                auto_rollback_if_needed(db, brand.id, platform)

            # 🔥 BRAND LEARNING HOOK (THIS IS THE BRAIN)
            print("🧠 [DEBUG] Running BrandMutationEngine...")
            engine = BrandMutationEngine(db)
            engine.evaluate_and_mutate(brand.id)

        print("\n✅ Performance Worker completed cycle")

    except Exception as e:
        print(f"❌ Performance Worker error: {e}")

    finally:
        db.close()
