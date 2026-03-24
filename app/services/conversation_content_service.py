from app.services.ai_generator import generate_content
from app.db.models import ContentItem, BrandProfile


def generate_content_item_from_plan(
    db,
    brand_id: int,
    plan: dict,
):

    brand = db.query(BrandProfile).filter(
        BrandProfile.id == brand_id
    ).first()

    if not brand:
        raise ValueError(f"Brand not found for brand_id={brand_id}")

    topic = plan.get("topic")

    extra_context = f"""
Story: {plan.get("story")}
Lesson: {plan.get("lesson")}
Angle: {plan.get("angle")}
Intent: {plan.get("intent")}
Tone: {plan.get("tone")}
Audience: {plan.get("audience")}
"""

    generated_text = generate_content(
        db,
        topic=topic,
        brand_id=brand_id,
        platform="linkedin",
        content_type="post",
        extra_context=extra_context,
    )

    # ✅ conversation pipeline should start as DRAFT
    status = "DRAFT"

    item = ContentItem(
        brand_id=brand_id,
        topic_id=None,
        platform="linkedin",
        content_type="post",
        content_text=generated_text,
        status=status,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item