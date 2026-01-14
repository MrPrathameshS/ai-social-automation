from fastapi import APIRouter
from app.db.session import SessionLocal
from app.db.models import GeneratedContent

router = APIRouter()

@router.post("/approve/{content_id}")
def approve_content(content_id: int):
    db = SessionLocal()
    content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()

    if not content:
        return {"error": "Content not found"}

    content.status = "approved"
    db.commit()
    db.close()

    return {"status": "approved", "content_id": content_id}
