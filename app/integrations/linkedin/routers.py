print("🔥 linkedin router module loading")


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
import secrets
import os
import requests
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


router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])

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
def linkedin_connect(
    brand: BrandProfile = Depends(get_current_brand),
):
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
    db_name = db.execute(text("SELECT current_database()")).scalar()
    print("🧠 BACKEND DB NAME =", db_name)
    search_path = db.execute(text("SHOW search_path")).scalar()
    print("🧠 BACKEND SEARCH_PATH =", search_path)
    server_addr = db.execute(text("SELECT inet_server_addr(), inet_server_port()")).all()
    print("🧠 BACKEND DB SERVER =", server_addr)

    count = db.execute(text("SELECT COUNT(*) FROM brand_profiles")).scalar()
    print("🧠 BACKEND BRAND COUNT =", count)



    # 🔍 DEBUG DB VISIBILITY
    brands = db.execute(
        text("SELECT id, brand_name FROM brand_profiles")
    ).fetchall()

    print("🔥 BRANDS IN CALLBACK DB =", brands)

    # ✅ Extract brand_id
    try:
        brand_id = int(state.split(":")[0])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    # ✅ Fetch brand
    brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # ✅ Exchange token
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
    access_token = token_res.json()["access_token"]

    # ✅ OIDC userinfo (CORRECT)
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

    # ✅ Save
    brand.linkedin_access_token = access_token
    brand.linkedin_author_urn = author_urn
    db.commit()

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
    if not brand.linkedin_access_token or not brand.linkedin_author_urn:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")

    ugc_payload = {
        "author": brand.linkedin_author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": payload.text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    res = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {brand.linkedin_access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=ugc_payload,
        timeout=15,
    )

    # 🔴 FAILURE PATH — NOW PERSISTED
    if res.status_code >= 400:
        # ✅ Persist failed post
        failed_post = LinkedInPost(
            brand_id=brand.id,
            linkedin_post_urn="FAILED",
            text=payload.text,
            status="failed",
            error_message=res.text,
        )

        db.add(failed_post)
        db.commit()
        db.refresh(failed_post)

        raise HTTPException(
            status_code=res.status_code,
            detail=res.text,
        )


    # ✅ SUCCESS PATH
    linkedin_post_urn = res.json().get("id")
    if not linkedin_post_urn:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected LinkedIn response: {res.json()}",
        )

    post = LinkedInPost(
        brand_id=brand.id,
        linkedin_post_urn=linkedin_post_urn,
        text=payload.text,
        status="published",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "status": "posted",
        "linkedin_post_urn": linkedin_post_urn,
        "post_id": post.id,
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

@router.post("/posts/{post_id}/retry")
def retry_linkedin_post(
    post_id: int,
    brand: BrandProfile = Depends(get_current_brand),
    db: Session = Depends(get_db),
):
    # 1️⃣ Fetch post (brand-scoped)
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

    # 2️⃣ Only failed posts can be retried
    if post.status != "failed":
        raise HTTPException(
            status_code=400,
            detail="Only failed posts can be retried",
        )

    # 3️⃣ Ensure LinkedIn is connected
    if not brand.linkedin_access_token or not brand.linkedin_author_urn:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")

    # 4️⃣ Rebuild LinkedIn payload
    ugc_payload = {
        "author": brand.linkedin_author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post.text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    # 5️⃣ Retry publish
    res = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {brand.linkedin_access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=ugc_payload,
        timeout=15,
    )

    if res.status_code >= 400:
        # 🔴 Still failed — update error
        post.error_message = res.text
        db.commit()

        raise HTTPException(status_code=res.status_code, detail=res.text)

    # 6️⃣ Success — update existing record
    linkedin_post_urn = res.json().get("id")
    if not linkedin_post_urn:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected LinkedIn response: {res.json()}",
        )

    post.linkedin_post_urn = linkedin_post_urn
    post.status = "published"
    post.error_message = None

    db.commit()
    db.refresh(post)

    return {
        "status": "retried",
        "post_id": post.id,
        "linkedin_post_urn": linkedin_post_urn,
    }
