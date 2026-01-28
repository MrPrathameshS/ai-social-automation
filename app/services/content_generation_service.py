from app.db.models import ContentItem, BrandProfile, Topic
from app.services.prompt_builder import build_brand_post_prompt
from app.services.brand_rule_prompt_builder import build_rule_prompt_layer
from app.core.llm import call_llm  # ✅ ONLY LLM ENTRY POINT
from app.core.content_status import DRAFT




def generate_content_for_topic(
    db,
    topic_id: int,
    platform: str,
    category_id: int | None = None
):
    # 1️⃣ Fetch topic
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise ValueError("Topic not found")

    # 2️⃣ Fetch brand
    brand = db.query(BrandProfile).filter(BrandProfile.id == topic.brand_id).first()
    if not brand:
        raise ValueError("Brand not found")

    # 3️⃣ Build base prompt
    learned_insights = brand.learned_insights
    base_prompt = build_brand_post_prompt(brand, topic, learned_insights)

    # 4️⃣ Build rule layer
    rule_prompt = build_rule_prompt_layer(
        db=db,
        brand_id=brand.id,
        platform=platform,
        category_id=category_id
    )

    # 5️⃣ Final system prompt
    system_prompt = f"""
You are a professional LinkedIn content writer.

{rule_prompt}

Follow all rules strictly.
Do not mention AI.
Do not explain the process.
""".strip()

    # 6️⃣ Call LLM (🔥 ONLY THROUGH llm.py)
    generated_text = call_llm(
        prompt=base_prompt,
        system_prompt=system_prompt
    )

    # 7️⃣ Persist content
    content_item = ContentItem(
        brand_id=brand.id,
        topic_id=topic.id,
        platform=platform,
        content_type="POST",
        content_text=generated_text,
        status=DRAFT
    )

    db.add(content_item)
    db.commit()
    db.refresh(content_item)

    # 8️⃣ Return product-safe response
    return {
        "status": "generation_completed",
        "content_id": content_item.id,
        "content_text": content_item.content_text
    }
