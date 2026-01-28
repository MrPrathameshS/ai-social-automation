from app.db.models import Topic, ContentItem
from app.db.session import SessionLocal
from app.services.sheets_service import get_sheet_data
from app.core.content_status import DRAFT

def ingest_from_sheet(sheet_name: str):
    db = SessionLocal()
    rows = get_sheet_data(sheet_name)

    for row in rows:
        topic_text = row["topic"]
        brand = row["brand"]
        platforms = row["platforms"].split(",")
        content_type = row["content_type"]

        # Create Topic
        topic = Topic(topic_text=topic_text, brand=brand)
        db.add(topic)
        db.commit()
        db.refresh(topic)

        # Create Content Items per platform
        for platform in platforms:
            from app.core.content_status import DRAFT

            item = ContentItem(
                topic_id=topic.id,
                platform=platform.strip(),
                content_type=content_type,
                status=DRAFT
            )

            db.add(item)

        db.commit()

    db.close()
