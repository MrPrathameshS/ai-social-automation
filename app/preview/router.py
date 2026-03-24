# app/preview/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.services.preview_generation_service import (
    generate_preview_from_insight,
    save_draft_from_insight,
)


router = APIRouter(
    prefix="/preview",
    tags=["preview"],
)


@router.post("/{session_id}/regenerate")
def generate_preview(
    session_id: int,
    db: Session = Depends(get_db),
):

    result = generate_preview_from_insight(
        db=db,
        session_id=session_id,
    )

    return result


@router.post("/{session_id}/save")
def save_draft(
    session_id: int,
    db: Session = Depends(get_db),
):

    result = save_draft_from_insight(
        db=db,
        session_id=session_id,
    )

    return result