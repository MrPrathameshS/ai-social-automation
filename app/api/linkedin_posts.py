from fastapi import APIRouter, Depends, HTTPException, logger, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models.linkedin_post import LinkedInPost
from app.db.models.brand_profile import BrandProfile

router = APIRouter(prefix="/linkedin/posts", tags=["LinkedIn Posts"])

MAX_RETRIES = 5


@router.post("/{post_id}/retry")
def retry_linkedin_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.query(LinkedInPost).filter(
        LinkedInPost.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.status == "published":
        raise HTTPException(
            status_code=400,
            detail="Post already published",
        )

    if post.status == "permanent_failure":
        raise HTTPException(
            status_code=400,
            detail="Post permanently failed. Create a new post.",
        )

    if post.retry_count >= MAX_RETRIES:
        raise HTTPException(
            status_code=400,
            detail="Max retries exceeded",
        )

    brand = db.query(BrandProfile).filter(
        BrandProfile.id == post.brand_id
    ).first()

    if not brand or brand.linkedin_disconnected_at:
        raise HTTPException(
            status_code=400,
            detail="LinkedIn disconnected. Reconnect required.",
        )

    # ✅ Requeue for worker
    post.status = "failed"
    post.next_retry_at = datetime.now(timezone.utc)
    post.last_error = None
    logger.info(
        "linkedin.post.manual_retry",
        extra={
            "post_id": post.id,
            "brand_id": post.brand_id,
            "retry_count": post.retry_count,
        },
    )

    db.commit()
    db.refresh(post)

    return {
        "id": post.id,
        "status": post.status,
        "retry_count": post.retry_count,
        "next_retry_at": post.next_retry_at,
        "published_at": post.published_at,
        "error_type": post.error_type,
    }

