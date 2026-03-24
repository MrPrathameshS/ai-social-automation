import time
import random
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.linkedin_post import LinkedInPost
from app.db.models.brand_profile import BrandProfile
from app.services.linkedin.publisher import LinkedInPublisher
from app.services.linkedin.errors import LinkedInAuthError
from datetime import timezone
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 30
BATCH_SIZE = 5
MAX_RETRIES = 5


# ==========================
# Retry Backoff
# ==========================
def compute_next_retry(retry_count: int) -> datetime:
    """
    Exponential backoff with jitter.
    """
    base_delay = 30  # seconds
    delay = base_delay * (2 ** retry_count)
    jitter = random.uniform(0.8, 1.2)
    return datetime.now(timezone.utc) + timedelta(seconds=delay * jitter)


# ==========================
# Brand Lifecycle
# ==========================
def mark_brand_disconnected(db: Session, brand_id: int):
    db.query(BrandProfile).filter(
        BrandProfile.id == brand_id
    ).update(
        {
            BrandProfile.linkedin_disconnected_at: datetime.now(timezone.utc),
            BrandProfile.linkedin_access_token: None,
            BrandProfile.linkedin_author_urn: None,
            BrandProfile.linkedin_token_expires_at: None,
        }
    )


# ==========================
# Worker Loop
# ==========================
def run_linkedin_retry_worker():
    logger.info(
        "linkedin.worker.started",
        extra={"source": "worker"},
    )


    while True:
        db: Session = SessionLocal()
        try:
            now = datetime.now(timezone.utc)

            # --------------------------
            # 1️⃣ Scheduled posts (first attempt)
            # --------------------------
            scheduled_posts = (
                db.query(LinkedInPost)
                .join(BrandProfile, LinkedInPost.brand_id == BrandProfile.id)
                .filter(
                    LinkedInPost.status == "pending",
                    LinkedInPost.scheduled_at.isnot(None),
                    LinkedInPost.scheduled_at <= now,
                    LinkedInPost.linkedin_post_urn.is_(None),
                )
                .order_by(LinkedInPost.scheduled_at.asc())
                .with_for_update(skip_locked=True)
                .limit(BATCH_SIZE)
                .all()
            )

            # --------------------------
            # 2️⃣ Retry posts
            # --------------------------
            retry_posts = (
                db.query(LinkedInPost)
                .join(BrandProfile, LinkedInPost.brand_id == BrandProfile.id)
                .filter(
                    LinkedInPost.status == "failed",
                    LinkedInPost.retry_count < MAX_RETRIES,
                    LinkedInPost.next_retry_at <= now,
                    LinkedInPost.linkedin_post_urn.is_(None),
                )
                .order_by(LinkedInPost.next_retry_at.asc())
                .with_for_update(skip_locked=True)
                .limit(BATCH_SIZE)
                .all()
            )

            posts = scheduled_posts + retry_posts
            publisher = LinkedInPublisher(db)

            for post in posts:
                is_retry = post.status == "failed"

                if is_retry:
                    post.retry_count += 1

                post.last_attempt_at = now
                db.flush()

                if not is_retry:
                    logger.info(
                        "linkedin.post.scheduled_triggered",
                        extra={
                            "post_id": post.id,
                            "brand_id": post.brand_id,
                            "source": "worker",
                        },
                    )

                else:
                    logger.info(
                        "linkedin.retry.attempt",
                        extra={
                            "post_id": post.id,
                            "brand_id": post.brand_id,
                            "retry_count": post.retry_count,
                            "source": "worker",
                        },
                    )


                try:
                    publisher.publish_text_post(
                        brand_id=post.brand_id,
                        text=post.text,
                        existing_post=post,
                    )

                    post.status = "published"
                    post.published_at = datetime.now(timezone.utc)
                    post.next_retry_at = None

                except LinkedInAuthError:
                    post.status = "permanent_failure"
                    post.last_error = "LinkedIn authorization expired"
                    post.next_retry_at = None
                    mark_brand_disconnected(db, post.brand_id)

                except Exception as e:
                    if post.retry_count >= MAX_RETRIES:
                        post.status = "permanent_failure"
                        post.last_error = "Max retries exceeded"

                        logger.error(
                            "linkedin.retry.permanent_failure",
                            extra={
                                "post_id": post.id,
                                "brand_id": post.brand_id,
                                "retry_count": post.retry_count,
                                "source": "worker",
                            },
                        )

                    else:
                        post.status = "failed"
                        post.last_error = str(e)
                        post.next_retry_at = compute_next_retry(post.retry_count)

            db.commit()

        except Exception:
            db.rollback()
            logger.exception(
                "linkedin.worker.loop_error",
                extra={"source": "worker"},
            )


        finally:
            db.close()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_linkedin_retry_worker()
