from sqlalchemy.orm import Session
from app.db.models import BrandProfile, BrandMutationLog
from app.core.llm import call_llm
from app.services.prompt_registry import regenerate_prompts_for_brand
from app.services.brand_performance_service import get_brand_performance_summary
import json
from decimal import Decimal


def serialize_for_json(obj):
    """
    Recursively convert Decimal and non-serializable objects into JSON-safe types.
    """
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_for_json(i) for i in obj]
    if isinstance(obj, Decimal):
        return float(obj)
    try:
        json.dumps(obj)
        return obj
    except:
        return str(obj)


class BrandMutationEngine:

    def __init__(self, db: Session):
        self.db = db

    def evaluate_and_mutate(self, brand_id: int):
        brand = self.db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
        if not brand:
            return

        performance = get_brand_performance_summary(self.db, brand_id)
        performance = serialize_for_json(performance)   # 🔥 CRITICAL FIX

        if not self._should_mutate(performance):
            print(f"🧠 [BrandMutation] No mutation needed for brand: {brand.brand_name}")
            return

        mutation_plan = self._ask_llm_for_mutation(brand, performance)
        self._apply_mutations(brand, mutation_plan, performance)

    def _should_mutate(self, performance: dict) -> bool:
        engagement_drop = performance.get("engagement_drop_percent", 0)
        consecutive_failures = performance.get("consecutive_failures", 0)

        if engagement_drop > 25:
            return True
        if consecutive_failures >= 3:
            return True

        return False

    def _ask_llm_for_mutation(self, brand: BrandProfile, performance: dict) -> dict:
        prompt = f"""
You are an expert brand strategist.

Brand Profile:
Tone: {brand.tone_description}
Audience: {brand.audience_description}
Writing Style: {brand.writing_style}
Do Not Use: {brand.do_not_use}

Learned Insights:
{brand.learned_insights}

Recent Performance Summary:
{json.dumps(performance, indent=2)}

Your task:
Identify which brand attributes should be adjusted to improve performance.
Only suggest changes that are strongly justified by the data.

Respond strictly in JSON format:
{{
  "mutations": [
    {{
      "field": "tone_description",
      "new_value": "...",
      "reason": "..."
    }}
  ]
}}
"""

        response = call_llm(prompt)

        def extract_json(text):
            text = text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
            return text.strip()

        try:
            clean = extract_json(response)
            parsed = json.loads(clean)
            return parsed
        except Exception as e:
            print("[BrandMutation] Failed to parse LLM response:", e)
            print("[BrandMutation] Raw response:", response)
            return {"mutations": []}


    def _apply_mutations(self, brand: BrandProfile, mutation_plan: dict, performance: dict):
        mutations = mutation_plan.get("mutations", [])

        for m in mutations:
            field = m.get("field")
            new_value = m.get("new_value")
            reason = m.get("reason")

            if not hasattr(brand, field):
                continue

            old_value = getattr(brand, field)

            log = BrandMutationLog(
                brand_id=brand.id,
                field_mutated=field,
                old_value=old_value,
                new_value=new_value,
                mutation_reason=reason,
                performance_snapshot=performance   # 🔥 now safe
            )
            self.db.add(log)

            setattr(brand, field, new_value)

            brand.learned_insights = (brand.learned_insights or "") + f"\n[MUTATION] {field}: {reason}"

        self.db.commit()

        if mutations:
            print(f"🧠 [BrandMutation] Applied {len(mutations)} mutations for brand: {brand.brand_name}")
            regenerate_prompts_for_brand(self.db, brand.id)
        else:
            print(f"🧠 [BrandMutation] No mutations returned by LLM for brand: {brand.brand_name}")
