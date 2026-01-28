from sqlalchemy.orm import Session
from app.db.models.topic import Topic


def create_manual_topic(db: Session, brand_id: int, topic_text: str):
    topic = Topic(
        topic_text=topic_text,
        brand_id=brand_id,
        source="MANUAL",
        status="NEW"
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def get_topics_for_brand(db: Session, brand_id: int):
    return db.query(Topic).filter(Topic.brand_id == brand_id).order_by(Topic.created_at.desc()).all()


def delete_topic(db: Session, topic: Topic):
    db.delete(topic)
    db.commit()


def update_topic_status(db: Session, topic: Topic, status: str):
    topic.status = status
    db.commit()
    db.refresh(topic)
    return topic
