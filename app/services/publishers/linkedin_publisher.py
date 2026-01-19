from app.db.models import ContentItem

class LinkedInPublishError(Exception):
    pass


def publish_to_linkedin(content: ContentItem) -> dict:
    """
    Publishes content to LinkedIn.
    Returns metadata on success.
    Raises LinkedInPublishError on failure.
    """

    # 🔒 Hard guard (defensive)
    if content.platform.lower() != "linkedin":
        raise LinkedInPublishError("Invalid platform for LinkedIn publisher")

    # 🔜 REAL IMPLEMENTATION COMES NEXT
    # For now, simulate success
    # This lets lifecycle logic be verified independently

    return {
        "platform": "linkedin",
        "external_post_id": "mock_linkedin_post_id",
        "url": "https://linkedin.com/feed/update/mock"
    }
