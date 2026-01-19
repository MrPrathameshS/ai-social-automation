from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def linkedin_health_check():
    return {"status": "linkedin integration alive"}


@router.post("/post")
def post_to_linkedin():
    """
    Placeholder endpoint.
    Later this will:
    - take approved content
    - push to LinkedIn API
    """
    return {"status": "posted to linkedin (stub)"}
