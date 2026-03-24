print("🔥 linkedin router module loading")

from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
import secrets
import os

from sqlalchemy import text

from app.db.session import get_db
from app.db.models import BrandProfile
from pydantic import BaseModel
from app.core.deps import get_current_brand
from app.schemas.linkedin_post import LinkedInPostResponse
from fastapi import Query
from sqlalchemy import func
from app.schemas.linkedin_post import (
    LinkedInPostResponse,
    LinkedInPostListResponse,
)

from sqlalchemy import and_
from datetime import datetime, date
from app.services.linkedin.publisher import LinkedInPublisher

import requests
router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])
from datetime import datetime, timedelta, timezone

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

print("🔎 LinkedIn ENV CHECK")
print("CLIENT_ID:", LINKEDIN_CLIENT_ID)
print("CLIENT_SECRET length:", len(LINKEDIN_CLIENT_SECRET or ""))
print("REDIRECT_URI:", LINKEDIN_REDIRECT_URI)


# ---------------------------
# Health
# ---------------------------
@router.get("/health")
def linkedin_health_check():
    return {"status": "linkedin integration alive"}


# ---------------------------
# OAuth Connect
# ---------------------------





#@router.get("/connect")
#def linkedin_connect(
#    brand: BrandProfile = Depends(get_current_brand),
#):
#    state = f"{brand.id}:{secrets.token_urlsafe(16)}"
#
#    auth_url = (
#        "https://www.linkedin.com/oauth/v2/authorization"
#        "?response_type=code"
#        f"&client_id={LINKEDIN_CLIENT_ID}"
#        f"&redirect_uri={quote(LINKEDIN_REDIRECT_URI, safe='')}"
#        "&scope=openid%20profile%20w_member_social"
#        f"&state={state}"
#        "&prompt=consent"
 #   )
#
#    return RedirectResponse(auth_url)

@router.get("/connect")
def linkedin_connect(db: Session = Depends(get_db)):

    # TEMP: pick the first brand for testing
    brand = db.query(BrandProfile).first()

    state = f"{brand.id}:{secrets.token_urlsafe(16)}"

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        "?response_type=code"
        f"&client_id={LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={quote(LINKEDIN_REDIRECT_URI, safe='')}"
        "&scope=openid%20profile%20w_member_social"
        f"&state={state}"
        "&prompt=consent"
    )

    return RedirectResponse(auth_url)



# ---------------------------
# OAuth Callback
# ---------------------------


@router.get("/callback")
def linkedin_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    print("🟠 CALLBACK")
    print("state received =", state)

    # ---------------------------
    # Debug / visibility (optional, safe)
    # ---------------------------
    db_name = db.execute(text("SELECT current_database()")).scalar()
    print("🧠 BACKEND DB NAME =", db_name)

    brands = db.execute(
        text("SELECT id, brand_name FROM brand_profiles")
    ).fetchall()
    print("🔥 BRANDS IN CALLBACK DB =", brands)

    # ---------------------------
    # Extract brand_id from state
    # ---------------------------
    try:
        brand_id = int(state.split(":")[0])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    brand = (
        db.query(BrandProfile)
        .filter(BrandProfile.id == brand_id)
        .first()
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # ---------------------------
    # Exchange authorization code → access token
    # ---------------------------
    token_res = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINKEDIN_REDIRECT_URI,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    token_res.raise_for_status()
    token_data = token_res.json()

    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in")  # seconds

    # ---------------------------
    # OIDC userinfo (MUST come BEFORE commit)
    # ---------------------------
    userinfo_res = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    userinfo_res.raise_for_status()
    userinfo = userinfo_res.json()

    person_id = userinfo.get("sub")
    if not person_id:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid userinfo response: {userinfo}",
        )

    author_urn = f"urn:li:person:{person_id}"

    # ---------------------------
    # Persist OAuth state atomically
    # ---------------------------
    now = datetime.now(timezone.utc)

    brand.linkedin_access_token = access_token
    brand.linkedin_author_urn = author_urn

    brand.linkedin_connected_at = now
    brand.linkedin_disconnected_at = None

    if expires_in:
        brand.linkedin_token_expires_at = now + timedelta(seconds=expires_in)
    else:
        brand.linkedin_token_expires_at = None

    db.commit()

    # ---------------------------
    # Redirect back to frontend
    # ---------------------------
    return RedirectResponse(
        url=f"{os.getenv('FRONTEND_URL')}/integrations/linkedin/success"
    )




# ---------------------------
# Post to LinkedIn
# ---------------------------
class LinkedInPostRequest(BaseModel):
    text: str


from app.db.models.linkedin_post import LinkedInPost




@router.post("/post")
def post_to_linkedin(
    payload: LinkedInPostRequest,
    brand: BrandProfile = Depends(get_current_brand),
    db: Session = Depends(get_db),
):
    # 🔒 PHASE 2: brand lifecycle guard
    if brand.linkedin_disconnected_at:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "LINKEDIN_DISCONNECTED",
                "message": "LinkedIn account disconnected. Reconnect required.",
                "action": "reconnect",
            },
        )

    # Existing credential guard (still valid)
    if not brand.linkedin_access_token or not brand.linkedin_author_urn:
        raise HTTPException(
            status_code=400,
            detail="LinkedIn not connected"
        )

    publisher = LinkedInPublisher(db)

    try:
        post = publisher.publish_text_post(
            brand=brand,
            text=payload.text,
        )

    except RuntimeError as e:
        if "authorization expired" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="LinkedIn authorization expired. Reconnect LinkedIn.",
            )
        raise

    if post.status == "failed":
        raise HTTPException(
            status_code=400,
            detail=post.error_message
        )

    return {
        "status": post.status,
        "post_id": post.id,
        "linkedin_post_urn": post.linkedin_post_urn,
        "retry_count": post.retry_count,
    }


@router.get(
    "/posts",
    response_model=LinkedInPostListResponse,
)
def list_linkedin_posts(
    brand: BrandProfile = Depends(get_current_brand),
    db: Session = Depends(get_db),

    # pagination
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),

    # filters
    status: str | None = Query(
        None,
        description="Filter by post status (published, failed)"
    ),
    from_date: date | None = Query(
        None,
        alias="from",
        description="Start date (YYYY-MM-DD)"
    ),
    to_date: date | None = Query(
        None,
        alias="to",
        description="End date (YYYY-MM-DD)"
    ),
):
    query = db.query(LinkedInPost).filter(
        LinkedInPost.brand_id == brand.id
    )

    # ✅ status filter
    if status:
        query = query.filter(LinkedInPost.status == status)

    # ✅ date filters
    if from_date:
        query = query.filter(
            LinkedInPost.published_at >= datetime.combine(from_date, datetime.min.time())
        )

    if to_date:
        query = query.filter(
            LinkedInPost.published_at <= datetime.combine(to_date, datetime.max.time())
        )

    total = query.count()

    posts = (
        query
        .order_by(LinkedInPost.published_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "items": posts,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

from datetime import datetime
from app.services.linkedin.publisher import LinkedInPublisher

@router.post("/posts/{post_id}/retry")
def retry_linkedin_post(
    post_id: int,
    brand: BrandProfile = Depends(get_current_brand),
    db: Session = Depends(get_db),
):
    post = (
        db.query(LinkedInPost)
        .filter(
            LinkedInPost.id == post_id,
            LinkedInPost.brand_id == brand.id,
        )
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 🚫 Permanent failure guard
    if post.status == "permanent_failure":
        raise HTTPException(
            status_code=400,
            detail="Post failed permanently. Reconnect LinkedIn to retry.",
        )

    # 🚫 Invalid state guard
    if post.status not in ("failed",):
        raise HTTPException(
            status_code=400,
            detail=f"Post is in '{post.status}' state and cannot be retried",
        )

    # ⏳ Backoff guard
    if post.next_retry_at and post.next_retry_at > datetime.utcnow():
        raise HTTPException(
            status_code=429,
            detail=f"Retry allowed after {post.next_retry_at.isoformat()}",
        )

    publisher = LinkedInPublisher(db)

    post = publisher.publish_text_post(
        brand=brand,
        text=post.text,
        existing_post=post,
    )

    return {
        "status": post.status,
        "post_id": post.id,
        "retry_count": post.retry_count,
        "next_retry_at": post.next_retry_at,
    }


