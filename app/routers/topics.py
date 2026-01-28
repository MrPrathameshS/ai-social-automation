from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.topic import TopicCreate, TopicResponse
from app.services import topic_service
from app.db.models.topic import Topic

router = APIRouter(prefix="/brands/{brand_id}/topics")



@router.post("/", response_model=TopicResponse)
def create_topic(brand_id: int, payload: TopicCreate, db: Session = Depends(get_db)):
    return topic_service.create_manual_topic(db, brand_id, payload.topic_text)


@router.get("/", response_model=list[TopicResponse])
def list_topics(brand_id: int, db: Session = Depends(get_db)):
    return topic_service.get_topics_for_brand(db, brand_id)


@router.delete("/{topic_id}")
def delete_topic(brand_id: int, topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.brand_id == brand_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic_service.delete_topic(db, topic)
    return {"status": "deleted"}
