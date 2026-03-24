import gspread
from google.oauth2.service_account import Credentials

from app.db.session import SessionLocal
from app.db.models import Topic, ContentItem

from app.services.ai_generator import generate_content


# 🔐 REQUIRED SCOPES (DO NOT CHANGE)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "credentials.json"
SHEET_NAME = "AI Social Automation Control"


def get_sheet_data():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1

    rows = sheet.get_all_records()
    print(f"📥 Fetched {len(rows)} rows from Google Sheet")
    return rows



def ingest_topics_from_sheet(rows):
    print("📥 Processing rows from Google Sheet...")
    db = SessionLocal()

    try:
        for row in rows:
            topic_text = row.get("topic")
            brand = row.get("brand")
            platforms = row.get("platforms")
            content_type = row.get("content_type", "post")
            approve = row.get("approve", "").strip().upper()

            if not topic_text or not platforms:
                continue

            # 1️⃣ Ensure topic exists
            topic = db.query(Topic).filter_by(topic_text=topic_text, brand=brand).first()
            if not topic:
                topic = Topic(topic_text=topic_text, brand=brand)
                db.add(topic)
                db.commit()
                db.refresh(topic)
                print(f"🆕 New topic added: {topic_text} [{brand}]")

            platform_list = [p.strip().lower() for p in platforms.split(",")]

            for platform in platform_list:
                existing = db.query(GeneratedContent).filter_by(
                    topic_id=topic.id,
                    platform=platform,
                    content_type=content_type
                ).first()

                # =========================
                # APPROVAL LOGIC
                # =========================

                if approve == "APPROVED":
                    if existing:
                        existing.status = "approved"
                        print(f"✅ Approved: {topic_text} [{platform}]")

                elif approve == "REJECTED":
                    print(f"🔁 Regenerating: {topic_text} [{platform}]")

                    new_text = generate_content(
                        topic=topic_text,
                        brand=brand,
                        platform=platform
                    )

                    if existing:
                        existing.content_text = new_text
                        existing.status = "pending"
                    else:
                        db.add(GeneratedContent(
                            topic_id=topic.id,
                            platform=platform,
                            content_type=content_type,
                            content_text=new_text,
                            status="pending"
                        ))

                else:
                    # NEW CONTENT GENERATION
                    if not existing:
                        print(f"🧠 Generating: {topic_text} [{platform}]")

                        generated = generate_content(
                            topic=topic_text,
                            brand=brand,
                            platform=platform
                        )

                        db.add(GeneratedContent(
                            topic_id=topic.id,
                            platform=platform,
                            content_type=content_type,
                            content_text=generated,
                            status="pending"
                        ))

        db.commit()
        print("✅ Sheet sync complete")

    except Exception as e:
        db.rollback()
        print(f"❌ Sheet ingestion error: {e}")
    finally:
        db.close()
