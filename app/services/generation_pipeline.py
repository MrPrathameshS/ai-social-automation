from app.services.ai_generator import generate_content
from app.services.prompt_registry import get_latest_prompt_record
from app.db.session import SessionLocal
from app.db.models import Topic, GeneratedContent

PLATFORMS = ["linkedin", "instagram"]


def run_generation_pipeline(brand_id: int):
    """
    Brand-isolated content generation pipeline.
    Only generates content for topics belonging to this brand.
    """

    db = SessionLocal()

    try:
        topics = db.query(Topic).filter(Topic.brand_id == brand_id).all()

        if not topics:
            print(f"⚠️ No topics found for brand_id={brand_id}")
            return

        for topic in topics:
            for platform in PLATFORMS:
                print(f"🧠 Generating content for brand_id={brand_id}, topic='{topic.topic_text}' on {platform}")

                prompt_record = get_latest_prompt_record(brand_id, platform)

                if not prompt_record:
                    print(f"⚠️ No prompt found for brand_id={brand_id} on {platform}, skipping...")
                    continue

                generated_text = generate_content(
                    topic=topic.topic_text,
                    brand_id=brand_id,
                    platform=platform,
                    content_type="post"
                )

                content_record = GeneratedContent(
                    client_id=topic.brand.client_id,
                    brand_id=brand_id,
                    topic_id=topic.id,
                    platform=platform,
                    content_type="post",
                    content_text=generated_text,
                    status="pending",
                    prompt_version=prompt_record.version
                )


                db.add(content_record)

        db.commit()
        print(f"✅ Generation complete for brand_id={brand_id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Generation pipeline error: {e}")
        raise
    finally:
        db.close()
