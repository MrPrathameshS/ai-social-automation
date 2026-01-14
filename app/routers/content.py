from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Topic
from app.api.deps import get_current_context
from app.services.ingestion_service import ingest_from_sheet
from app.services.generation_pipeline import run_generation_pipeline
from pydantic import BaseModel


router = APIRouter(prefix="/content", tags=["content"])


# =========================
# Schemas
# =========================

class TopicCreateRequest(BaseModel):
    topic_text: str


class IngestRequest(BaseModel):
    sheet_name: str


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
    ctx: dict = Depends(get_current_context)
):
    """
    Brand-isolated generation trigger.
    """
    run_generation_pipeline(ctx["brand_id"])
    return {"status": "generation_started", "brand_id": ctx["brand_id"]}
