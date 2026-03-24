import gspread
from google.oauth2.service_account import Credentials

from app.db.session import SessionLocal
from app.db.models import Topic, GeneratedContent


# Path to your service account json
SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_gsheet_client():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(creds)


def ingest_from_google_sheet(sheet_name: str):
    print("📥 Ingesting data from Google Sheet...")
    client = get_gsheet_client()
    sheet = client.open(sheet_name).sheet1

    rows = sheet.get_all_records()

    db = SessionLocal()

    try:
        for idx, row in enumerate(rows, start=2):  # start=2 because header is row 1
            topic_text = row.get("topic")
            brand = row.get("brand")
            platforms = row.get("platforms")
            content_type = row.get("content_type")
            status = row.get("status", "").lower()
            approve = row.get("approve", "").lower()

            if not topic_text or not platforms:
                continue

            # 1. Upsert Topic
            topic = (
                db.query(Topic)
                .filter(Topic.topic_text == topic_text, Topic.brand == brand)
                .first()
            )

            if not topic:
                topic = Topic(topic_text=topic_text, brand=brand)
                db.add(topic)
                db.commit()
                db.refresh(topic)
                print(f"🆕 Created topic: {topic_text}")

            # 2. Create GeneratedContent per platform
            platform_list = [p.strip().lower() for p in platforms.split(",")]

            for platform in platform_list:
                existing = (
                    db.query(GeneratedContent)
                    .filter(
                        GeneratedContent.topic_id == topic.id,
                        GeneratedContent.platform == platform,
                        GeneratedContent.content_type == content_type
                    )
                    .first()
                )

                if existing:
                    continue

                content = GeneratedContent(
                    topic_id=topic.id,
                    platform=platform,
                    content_type=content_type,
                    status="approved" if approve == "yes" else "pending"
                )

                db.add(content)
                print(f"➕ Added content: {topic_text} → {platform}")

        db.commit()
        print("✅ Google Sheet ingestion complete")

    except Exception as e:
        print(f"❌ Sheet ingestion error: {e}")
        db.rollback()
    finally:
        db.close()
