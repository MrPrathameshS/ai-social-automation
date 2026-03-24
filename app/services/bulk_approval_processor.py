from app.db.session import SessionLocal
from app.db.models import GeneratedContent, Topic
from app.services.ai_generator import generate_content
from app.services.ai_scheduler import run_ai_scheduler
from app.services.sheets_service import get_sheet_rows
from app.services.sheets_status_sync import sync_db_status_to_sheet


def run_bulk_approval_engine():
    print("🚀 BULK APPROVAL ENGINE STARTED")

    db = SessionLocal()

    try:
        rows = get_sheet_rows()
        print(f"📥 Fetched {len(rows)} rows from sheet")

        topics = db.query(Topic).all()
        topic_map = {t.topic_text: t.id for t in topics}

        for row in rows:
            topic_text = row.get("topic", "").strip()
            brand = row.get("brand", "").strip()
            platforms_raw = row.get("platforms", "")
            content_type = row.get("content_type", "").strip()
            approve_status = row.get("approve", "").strip().upper()

            if not topic_text or not platforms_raw:
                continue

            platform_list = [p.strip().lower() for p in platforms_raw.split(",")]

            # Ensure topic exists
            if topic_text not in topic_map:
                topic_obj = Topic(topic_text=topic_text, brand=brand)
                db.add(topic_obj)
                db.commit()
                db.refresh(topic_obj)
                topic_map[topic_text] = topic_obj.id
                print(f"🆕 Created topic: {topic_text}")

            topic_id = topic_map[topic_text]

            for platform in platform_list:
                existing = db.query(GeneratedContent).filter_by(
                    topic_id=topic_id,
                    platform=platform
                ).first()

                # ---------------- APPROVED ----------------
                if approve_status == "APPROVED":
                    if existing:
                        existing.status = "approved"
                        print(f"✅ Approved existing: {topic_text} [{platform}]")
                    else:
                        print(f"🧠 Generating (approved): {topic_text} [{platform}]")
                        generated_text = generate_content(
                            topic=topic_text,
                            brand=brand,
                            platform=platform
                        )

                        db.add(GeneratedContent(
                            topic_id=topic_id,
                            platform=platform,
                            content_type=content_type,
                            content_text=generated_text,
                            status="approved"
                        ))

                # ---------------- REJECTED ----------------
                elif approve_status == "REJECTED":
                    print(f"🔁 Regenerating (rejected): {topic_text} [{platform}]")
                    regenerated_text = generate_content(
                        topic=topic_text,
                        brand=brand,
                        platform=platform
                    )

                    if existing:
                        existing.content_text = regenerated_text
                        existing.status = "pending"
                    else:
                        db.add(GeneratedContent(
                            topic_id=topic_id,
                            platform=platform,
                            content_type=content_type,
                            content_text=regenerated_text,
                            status="pending"
                        ))

                # ---------------- EMPTY / NEW ----------------
                else:
                    if not existing:
                        print(f"🧠 Generating (new): {topic_text} [{platform}]")
                        generated_text = generate_content(
                            topic=topic_text,
                            brand=brand,
                            platform=platform
                        )

                        db.add(GeneratedContent(
                            topic_id=topic_id,
                            platform=platform,
                            content_type=content_type,
                            content_text=generated_text,
                            status="pending"
                        ))

        db.commit()

        print("📤 Triggering AI Scheduler...")
        run_ai_scheduler()

        print("🔄 Syncing status back to sheet...")
        sync_db_status_to_sheet()

        print("✅ BULK APPROVAL ENGINE COMPLETE")

    except Exception as e:
        db.rollback()
        print(f"❌ BULK APPROVAL ENGINE ERROR: {e}")
    finally:
        db.close()

def apply_bulk_action(action, topic, brand, platforms, db):
    action = action.strip().upper()

    query = db.query(GeneratedContent)

    if topic:
        query = query.join(Topic).filter(Topic.topic_text == topic)

    if brand:
        query = query.join(Topic).filter(Topic.brand == brand)

    if platforms:
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        query = query.filter(GeneratedContent.platform.in_(platform_list))

    items = query.all()

    print(f"🔧 Applying action '{action}' to {len(items)} items")

    # --- ACTION ROUTER ---
    if action == "APPROVE_ALL":
        for item in items:
            item.status = "approved"

    elif action.startswith("APPROVE_"):
        platform = action.replace("APPROVE_", "").lower()
        for item in items:
            if item.platform == platform:
                item.status = "approved"

    elif action == "REJECT_ALL":
        for item in items:
            item.status = "rejected"

    elif action.startswith("REJECT_PLATFORM:"):
        platform = action.split(":")[1].lower()
        for item in items:
            if item.platform == platform:
                item.status = "rejected"

    elif action == "REGENERATE":
        for item in items:
            print(f"🔁 Regenerating content ID {item.id}")
            new_text = generate_content(
                topic=item.topic.topic_text,
                brand=item.topic.brand,
                platform=item.platform
            )
            item.content_text = new_text
            item.status = "pending"

    else:
        print(f"⚠️ Unknown action: {action}")

    db.commit()
