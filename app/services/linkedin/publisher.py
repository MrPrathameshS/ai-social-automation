from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.models.linkedin_post import LinkedInPost
from app.services.linkedin.client import LinkedInClient, LinkedInAPIError
from app.services.linkedin.errors import classify_linkedin_error
from app.services.linkedin.errors import LinkedInAuthError

MAX_RETRIES = 5


# ==========================
# Domain Exceptions
# ==========================
class LinkedInAuthExpired(Exception):
    """Raised when LinkedIn token is expired before making an API call."""
    pass


class LinkedInPublisher:
    def __init__(self, db: Session):
        self.db = db

    def publish_text_post(
        self,
        brand,
        text: str,
        *,
        existing_post: LinkedInPost | None = None,
    ) -> LinkedInPost:

        now = datetime.now(timezone.utc)

        # ==========================
        # 🔒 HARD AUTH GUARD (TEST 1)
        # ==========================
        if brand.linkedin_token_expires_at and brand.linkedin_token_expires_at <= now:
            self._disconnect_brand(brand)
            self.db.commit()
            raise LinkedInAuthExpired()

        # ==========================
        # 🔁 Create or reuse post
        # ==========================
        post = existing_post or LinkedInPost(
            brand_id=brand.id,
            text=text,
            status="pending",
            retry_count=0,
        )

        if not existing_post:
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)

        client = LinkedInClient(brand.linkedin_access_token)

        try:
            urn = client.create_text_post(
                author_urn=brand.linkedin_author_urn,
                text=text,
            )

            post.linkedin_post_urn = urn
            post.status = "published"
            post.error_message = None
            post.error_type = None
            post.next_retry_at = None

        except LinkedInAPIError as e:
            error_type = classify_linkedin_error(
                e.status_code,
                str(e.payload),
            )

            post.error_message = str(e)
            post.error_type = error_type

            if error_type == "auth_error":
                self._disconnect_brand(brand)
                raise LinkedInAuthError("LinkedIn authorization expired")

            raise e


        self.db.commit()
        self.db.refresh(post)
        return post

    # ==========================
    # Helpers
    # ==========================
    def _disconnect_brand(self, brand):
        brand.linkedin_access_token = None
        brand.linkedin_author_urn = None
        brand.linkedin_token_expires_at = None
        brand.linkedin_disconnected_at = datetime.now(timezone.utc)

    def _calculate_backoff(self, retry_count: int) -> timedelta:
        # 30s, 60s, 120s, 240s, 480s (cap at 10 min)
        seconds = min(30 * (2 ** retry_count), 600)
        return timedelta(seconds=seconds)
