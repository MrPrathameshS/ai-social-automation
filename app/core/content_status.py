# app/core/content_status.py

# Canonical content states
DRAFT = "DRAFT"
PENDING_APPROVAL = "PENDING_APPROVAL"
APPROVED = "APPROVED"
PUBLISHED = "PUBLISHED"
FAILED = "FAILED"

ALL_STATUSES = {
    DRAFT,
    PENDING_APPROVAL,
    APPROVED,
    PUBLISHED,
    FAILED,
}

# app/core/content_status.py

ALLOWED_TRANSITIONS = {
    DRAFT: {DRAFT, PENDING_APPROVAL},
    PENDING_APPROVAL: {APPROVED, DRAFT},
    APPROVED: {PUBLISHED, DRAFT},
    PUBLISHED: set(),        # terminal
    FAILED: set(),           # terminal
}
