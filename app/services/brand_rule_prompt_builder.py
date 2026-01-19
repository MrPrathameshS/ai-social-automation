from sqlalchemy.orm import Session
from collections import defaultdict
from app.services.brand_rule_service import get_active_rules

# 🔥 Rule execution priority (v1)
RULE_PRIORITY = [
    "ASSERTIVENESS",
    "TONE",
    "CTA_STYLE",
    "LENGTH",
    "EMOJI_POLICY",
]

def build_rule_prompt_layer(
    db: Session,
    brand_id: int,
    platform: str,
    category_id: int | None = None
) -> str:
    rules = get_active_rules(db, brand_id, platform, category_id)

    if not rules:
        return ""

    grouped_rules = defaultdict(list)

    for rule in rules:
        grouped_rules[rule.rule_type].append(rule.rule_text)

    sections = []

    # 🔥 Apply deterministic ordering
    for rule_type in RULE_PRIORITY:
        if rule_type not in grouped_rules:
            continue

        lines = "\n".join(f"- {text}" for text in grouped_rules[rule_type])
        sections.append(f"{rule_type} RULES:\n{lines}")

    rule_block = "\n\n".join(sections)

    return f"""
FOUNDER MODE – BRAND RULES (STRICT):

You are writing for a solo consultant or founder.
Authority and clarity matter more than politeness.
Follow ALL rules below exactly, in order.

{rule_block}

Any response that violates these rules is invalid.
""".strip()
