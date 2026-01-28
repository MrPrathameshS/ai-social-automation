from fastapi import HTTPException
from app.core.content_status import (
    DRAFT,
    PENDING_APPROVAL,
    APPROVED,
    PUBLISHED,
    FAILED,
)

ALLOWED_TRANSITIONS = {
    DRAFT: {PENDING_APPROVAL},
    PENDING_APPROVAL: {APPROVED, DRAFT},
    APPROVED: {PUBLISHED, DRAFT},
    PUBLISHED: set(),
    FAILED: set(),
}

def assert_valid_transition(current: str, next_: str):
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if next_ not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current} → {next_}"
        )
