from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ContentItem

router = APIRouter()


@router.post("/approve/{content_id}")
def approve_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.status = "APPROVED"
    db.commit()
    db.refresh(content)

    return {
        "status": "approved",
        "content_id": content.id,
        "platform": content.platform,
        "content_type": content.content_type
    }
