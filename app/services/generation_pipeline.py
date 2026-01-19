from app.services.ai_generator import generate_content
from app.services.prompt_registry import get_latest_prompt_record
from app.db.models import Topic, ContentItem, BrandProfile

PLATFORMS = ["linkedin"]  # start with one, expand later


def run_generation_pipeline(db, brand_id: int):
    """
    Brand-isolated content generation pipeline.
    Only generates content for topics belonging to this brand.
    """

    try:
        # 1️⃣ Load brand (for approval logic)
        brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()

        if not brand:
            print(f"❌ Brand not found for brand_id={brand_id}")
            return

        # 2️⃣ Fetch topics for this brand
        topics = db.query(Topic).filter(Topic.brand_id == brand_id).all()

        if not topics:
            print(f"⚠️ No topics found for brand_id={brand_id}")
            return

        for topic in topics:
            for platform in PLATFORMS:

                # 3️⃣ Avoid duplicate generation (very important)
                existing = db.query(ContentItem).filter(
                    ContentItem.brand_id == brand_id,
                    ContentItem.topic_id == topic.id,
                    ContentItem.platform == platform,
                    ContentItem.content_type == "post"
                ).first()

                if existing:
                    print(f"⏭️ Skipping existing content for topic='{topic.topic_text}' on {platform}")
                    continue

                print(f"🧠 Generating content for brand_id={brand_id}, topic='{topic.topic_text}' on {platform}")

                # 4️⃣ Get prompt
                prompt_record = get_latest_prompt_record(brand_id, platform)

                if not prompt_record:
                    print(f"⚠️ No prompt found for brand_id={brand_id} on {platform}, skipping...")
                    continue

                # 5️⃣ Generate content
                generated_text = generate_content(
                    topic=topic.topic_text,
                    brand_id=brand_id,
                    platform=platform,
                    content_type="post"
                )

                # 6️⃣ Approval logic (CRITICAL)
                status = "PENDING_APPROVAL" if brand.approval_required else "APPROVED"

                # 7️⃣ Save content
                content_record = ContentItem(
                    brand_id=brand_id,
                    topic_id=topic.id,
                    platform=platform,
                    content_type="post",
                    content_text=generated_text,
                    status=status
                )

                db.add(content_record)

        db.commit()
        print(f"✅ Generation complete for brand_id={brand_id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Generation pipeline error: {e}")
        raise
