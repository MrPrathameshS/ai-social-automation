# app/services/insight_generation_service.py

from sqlalchemy.orm import Session

from app.db.models import Topic, BrandProfile, Insight

from app.services.content_generation_service import generate_content_for_topic


def generate_from_insight(
    db: Session,
    session_id: int,
    platform: str = "LINKEDIN",
):
    """
    Generate content using latest insight from conversation
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

    # 2️⃣ get brand (for now first brand)
    brand = db.query(BrandProfile).first()

    if not brand:
        raise ValueError("Brand not found")

    # 3️⃣ create topic from insight

    topic = Topic(
        brand_id=brand.id,
        title=insight.topic,
        description=f"""
Challenge: {insight.challenge}
Lesson: {insight.lesson}
Angle: {insight.angle}
""",
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    # 4️⃣ call existing generator

    result = generate_content_for_topic(
        db=db,
        topic_id=topic.id,
        platform=platform,
    )

    return result