from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import Topic, ContentItem
from app.api.deps import get_current_context
from app.schemas.content import ContentGenerateRequest
from app.services.ingestion_service import ingest_from_sheet
from app.services.content_generation_service import generate_content_for_topic


from app.core.content_guards import assert_valid_transition
from app.core.content_status import (
    DRAFT,
    PENDING_APPROVAL,
    APPROVED,
    PUBLISHED,
    FAILED,
)
from app.services.publishers.linkedin_api import (
    publish_to_linkedin,
    LinkedInPublishError,
)


router = APIRouter(tags=["content"])


# =========================
# Schemas
# =========================

class TopicCreateRequest(BaseModel):
    topic_text: str


class IngestRequest(BaseModel):
    sheet_name: str

class ContentEditRequest(BaseModel):
    content_text: str


class RejectRequest(BaseModel):
    reason: str | None = None

# =========================
# Endpoints
# =========================

@router.get("/topics")
def get_topics(
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context)
):
    brand_id = ctx["brand_id"]

    topics = db.query(Topic).filter(Topic.brand_id == brand_id).all()
    return topics


@router.post("/topics")
def create_topic(
    payload: TopicCreateRequest,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context)
):
    topic = Topic(
        topic_text=payload.topic_text,
        brand_id=ctx["brand_id"]
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.post("/ingest")
def ingest(
    payload: IngestRequest,
    ctx: dict = Depends(get_current_context)
):
    """
    Brand-isolated ingestion.
    """
    ingest_from_sheet(payload.sheet_name, brand_id=ctx["brand_id"])
    return {"status": "Ingestion completed", "brand_id": ctx["brand_id"]}


@router.post("/generate")
def generate_for_my_brand(
    payload: ContentGenerateRequest,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context)
):
    print("DEBUG payload.platform:", payload.platform, type(payload.platform))

    result = generate_content_for_topic(
        db=db,
        topic_id=payload.topic_id,
        platform=payload.platform,
        category_id=payload.category_id
    )

    return result

@router.post("/{content_id}/submit")
def submit_for_approval(
    content_id: int,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context),
):
    print("CTX brand_id:", ctx["brand_id"])

    brand_id = ctx["brand_id"]

    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.brand_id == brand_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    assert_valid_transition(content.status, PENDING_APPROVAL)

    content.status = PENDING_APPROVAL
    db.commit()

    return {"status": "submitted", "content_id": content.id}

@router.post("/{content_id}/approve")
def approve_content(
    content_id: int,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context),
):
    brand_id = ctx["brand_id"]

    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.brand_id == brand_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # ✅ Guard: only PENDING_APPROVAL → APPROVED
    assert_valid_transition(content.status, APPROVED)

    content.status = APPROVED
    content.approved_at = datetime.now(timezone.utc)

    db.commit()

    return {"status": "approved", "content_id": content.id}

@router.post("/{content_id}/reject")
def reject_content(
    content_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context),
):
    brand_id = ctx["brand_id"]

    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.brand_id == brand_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    assert_valid_transition(content.status, DRAFT)

    content.status = DRAFT
    db.commit()

    return {"status": "rejected", "content_id": content.id}

@router.patch("/{content_id}")
def edit_content(
    content_id: int,
    payload: ContentEditRequest,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context),
):
    brand_id = ctx["brand_id"]

    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.brand_id == brand_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Editing is allowed in DRAFT or APPROVED
    if content.status == APPROVED:
        assert_valid_transition(APPROVED, DRAFT)
        content.status = DRAFT

    elif content.status != DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Content can only be edited in DRAFT or APPROVED state"
        )


    content.content_text = payload.content_text
    db.commit()


    return {"status": "updated", "content_id": content.id}

from app.services.publishers.linkedin_api import (
    publish_to_linkedin,
    LinkedInPublishError,
)

@router.post("/{content_id}/publish")
def publish_content(
    content_id: int,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context),
):
    brand_id = ctx["brand_id"]

    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.brand_id == brand_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 🔒 Guard: only APPROVED → PUBLISHED
    assert_valid_transition(content.status, PUBLISHED)

    # 🔒 Idempotency guard (very important)
    if content.linkedin_post_urn:
        raise HTTPException(
            status_code=400,
            detail="Content already published to LinkedIn"
        )

    try:
        # ✅ Call real LinkedIn publisher
        result = publish_to_linkedin(content)

        # ✅ Persist success
        content.status = PUBLISHED
        content.published_at = datetime.now(timezone.utc)
        content.linkedin_post_urn = result["external_post_id"]
        content.publish_error = None

        db.commit()

        return {
            "status": "published",
            "content_id": content.id,
            "published_at": content.published_at,
            "linkedin_post_urn": content.linkedin_post_urn,
            "linkedin_url": result["url"],
        }

    except LinkedInPublishError as e:
        # 🔴 Platform failure (recoverable)
        content.status = FAILED
        content.publish_error = str(e)
        db.commit()

        raise HTTPException(
            status_code=502,
            detail=f"LinkedIn publishing failed: {str(e)}"
        )

    except Exception as e:
        # 🔴 Unexpected failure
        content.status = FAILED
        content.publish_error = str(e)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Unexpected publishing error"
        )


@router.post("/{content_id}/publish-now")
def publish_now(
    content_id: int,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_current_context),
):
    brand_id = ctx["brand_id"]

    content = (
        db.query(ContentItem)
        .filter(
            ContentItem.id == content_id,
            ContentItem.brand_id == brand_id,
        )
        .first()
    )

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 🔒 Guard: only APPROVED content
    assert_valid_transition(content.status, PUBLISHED)

    brand = content.brand

    if not brand.is_active:
        raise HTTPException(
            status_code=400,
            detail="Brand is inactive (auth failure or disabled)",
        )

    if not brand.linkedin_access_token or not brand.linkedin_author_urn:
        raise HTTPException(
            status_code=400,
            detail="Missing LinkedIn credentials",
        )

    router = PublisherRouter()
    now = datetime.now(timezone.utc)

    try:
        result = router.publish(
            content=content,
            access_token=brand.linkedin_access_token,
            author_urn=brand.linkedin_author_urn,
        )

        content.status = PUBLISHED
        content.published_at = now
        content.linkedin_post_urn = result["external_post_id"]
        content.publish_error = None

        db.commit()

        return {
            "status": "published",
            "content_id": content.id,
            "linkedin_post_urn": content.linkedin_post_urn,
            "published_at": content.published_at,
        }

    except PublishError as e:
        content.publish_error = str(e)

        if e.error_type == PublishErrorType.AUTH:
            content.status = FAILED
            brand.is_active = False

        elif e.retryable:
            content.status = FAILED
            content.retry_count += 1
            content.last_retry_at = now

        else:
            content.status = FAILED

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Publish failed: {str(e)}",
        )


