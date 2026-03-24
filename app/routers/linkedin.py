from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_brand
from app.db.session import get_db
from app.db.models.brand_profile import BrandProfile
from app.schemas.linkedin_post import LinkedInPostRequest
from app.services.linkedin.publisher import LinkedInPublisher




router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])



@router.post("/post")
def post_to_linkedin(
    payload: LinkedInPostRequest,
    brand: BrandProfile = Depends(get_current_brand),
    db: Session = Depends(get_db),
):
    if not brand.linkedin_access_token or not brand.linkedin_author_urn:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")

    publisher = LinkedInPublisher(db)
    post = publisher.publish_text_post(
        brand=brand,
        text=payload.text,
    )

    if post.status == "failed":
        raise HTTPException(status_code=400, detail=post.error_message)

    if post.status == "permanent_failure":
        raise HTTPException(
            status_code=400,
            detail="LinkedIn authorization expired. Reconnect LinkedIn.",
        )

    return {
        "status": post.status,
        "post_id": post.id,
        "linkedin_post_urn": post.linkedin_post_urn,
    }
