# app/services/preview_generation_service.py

from sqlalchemy.orm import Session

from app.db.models import Insight, BrandProfile

from app.core.llm import call_llm
from app.services.prompt_builder import build_brand_post_prompt
from app.services.brand_rule_prompt_builder import build_rule_prompt_layer


def generate_preview_from_insight(
    db: Session,
    session_id: int,
    platform: str = "LINKEDIN",
    category_id: int | None = None,
):
    """
    Generate preview text from insight without saving ContentItem
    """

    # 1️⃣ get latest insight
    insight = (
        db.query(Insight)
        .filter(Insight.session_id == session_id)
        .order_by(Insight.id.desc())
        .first()
    )

    if not insight:
        raise ValueError("Insight not found")

    # 2️⃣ get brand
    brand = db.query(BrandProfile).first()

    if not brand:
        raise ValueError("Brand not found")

    # 3️⃣ build pseudo topic object for prompt builder

    class TempTopic:

        title = insight.topic

        topic_text = insight.topic

        description = f"""
    Challenge: {insight.challenge}
    Lesson: {insight.lesson}
    Angle: {insight.angle}
    """

        brand_id = brand.id

    temp_topic = TempTopic()

    # 4️⃣ build prompt using existing pipeline

    learned_insights = brand.learned_insights

    base_prompt = build_brand_post_prompt(
        brand,
        temp_topic,
        learned_insights,
    )

    rule_prompt = build_rule_prompt_layer(
        db=db,
        brand_id=brand.id,
        platform=platform,
        category_id=category_id,
    )

    system_prompt = f"""
You are a professional LinkedIn content writer.

{rule_prompt}

Follow all rules strictly.
Do not mention AI.
Do not explain the process.
""".strip()

    # 5️⃣ call LLM

    generated_text = call_llm(
        prompt=base_prompt,
        system_prompt=system_prompt,
    )

    # 6️⃣ return preview only

    return {
        "status": "preview_generated",
        "text": generated_text,
        "session_id": session_id,
    }

from app.db.models import Topic
from app.services.content_generation_service import generate_content_for_topic


def save_draft_from_insight(
    db,
    session_id: int,
    platform: str = "LINKEDIN",
):
    """
    Convert insight → topic → draft using existing generator
    """

    # 1️⃣ get insight
    insight = (
        db.query(Insight)
        .filter(Insight.session_id == session_id)
        .order_by(Insight.id.desc())
        .first()
    )

    if not insight:
        raise ValueError("Insight not found")

    # 2️⃣ get brand
    brand = db.query(BrandProfile).first()

    if not brand:
        raise ValueError("Brand not found")

    # 3️⃣ create topic

    topic = Topic(
        brand_id=brand.id,
        topic_text=insight.topic,
        source="CONVERSATION",
        status="NEW",
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)


    # 4️⃣ generate content using existing pipeline

    result = generate_content_for_topic(
        db=db,
        topic_id=topic.id,
        platform=platform,
    )

    return result