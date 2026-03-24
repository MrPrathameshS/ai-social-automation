from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import ContentItem
from app.core.content_status import APPROVED, PUBLISHED, FAILED
from app.services.publishers.router import PublisherRouter
from app.services.publishers.base import PublishError
from app.services.publishers.errors import PublishErrorType

MAX_RETRIES = 5

BACKOFF_SCHEDULE = [
    60,        # 1 min
    300,       # 5 min
    900,       # 15 min
    3600,      # 1 hour
    21600,     # 6 hours
]


def publish_due_content():
    print("⏰ Scheduler tick:", datetime.now(timezone.utc))
    db: Session = SessionLocal()
    router = PublisherRouter()

    try:
        now = datetime.now(timezone.utc)

        items = (
            db.query(ContentItem)
            .filter(
                ContentItem.status.in_([APPROVED, FAILED]),
                ContentItem.scheduled_for.isnot(None),
                ContentItem.scheduled_for <= now,
                ContentItem.linkedin_post_urn.is_(None),
            )
            .all()
        )

        for content in items:

            if content.retry_count >= MAX_RETRIES:
                continue

            if content.last_retry_at:
                backoff = BACKOFF_SCHEDULE[
                    min(content.retry_count, len(BACKOFF_SCHEDULE) - 1)
                ]
                if now < content.last_retry_at + timedelta(seconds=backoff):
                    continue

            try:
                brand = content.brand

                if not brand.linkedin_access_token or not brand.linkedin_author_urn:
                    raise PublishError("Missing platform credentials")

                result = router.publish(
                    content=content,
                    access_token=brand.linkedin_access_token,
                    author_urn=brand.linkedin_author_urn,
                )

                content.status = PUBLISHED
                content.published_at = now
                content.linkedin_post_urn = result["external_post_id"]
                content.publish_error = None

            except PublishError as e:
                content.publish_error = str(e)

                # 🔐 Auth failure → disable brand, stop retries
                if e.error_type == PublishErrorType.AUTH:
                    content.status = FAILED
                    content.brand.is_active = False
                    continue

                # ❌ Non-retryable error → fail permanently
                if not e.retryable:
                    content.status = FAILED
                    continue

                # ⏳ Retryable error → retry with backoff
                content.retry_count += 1
                content.last_retry_at = now
                content.status = FAILED


        db.commit()

    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        publish_due_content,
        trigger="interval",
        seconds=60,
        id="publish_due_content",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
    print("✅ Scheduler started: publish_due_content runs every 60 seconds")
