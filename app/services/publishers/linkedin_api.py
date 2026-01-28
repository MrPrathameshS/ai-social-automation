import requests
from app.db.models import ContentItem
from app.core.platform import Platform
from app.services.publishers.base import PublishError
from app.services.publishers.errors import PublishErrorType

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"


class LinkedInPublishError(PublishError):
    pass


def publish_to_linkedin(
    content: ContentItem,
    access_token: str,
    author_urn: str,
) -> dict:
    """
    Publishes content to LinkedIn.
    Returns metadata on success.
    Raises LinkedInPublishError on failure.
    """

    # 🔒 Platform guard
    if content.platform != Platform.LINKEDIN:
        raise LinkedInPublishError(
            "Invalid platform for LinkedIn publisher",
            error_type=PublishErrorType.CLIENT,
            retryable=False,
        )

    # 🔒 Idempotency guard
    if content.linkedin_post_urn:
        raise LinkedInPublishError(
            "Content already published to LinkedIn",
            error_type=PublishErrorType.CLIENT,
            retryable=False,
        )

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content.content_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "X-Request-Id": f"content-{content.id}",
    }

    try:
        response = requests.post(
            LINKEDIN_POST_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
    except requests.RequestException as e:
        raise LinkedInPublishError(
            f"Network error: {str(e)}",
            error_type=PublishErrorType.SERVER,
            retryable=True,
        )

    # 🔐 Auth errors
    if response.status_code in (401, 403):
        raise LinkedInPublishError(
            "LinkedIn auth failed",
            error_type=PublishErrorType.AUTH,
            retryable=False,
        )

    # ⏳ Rate limit
    if response.status_code == 429:
        raise LinkedInPublishError(
            "LinkedIn rate limit exceeded",
            error_type=PublishErrorType.RATE_LIMIT,
            retryable=True,
        )

    # 🔥 Server errors
    if 500 <= response.status_code < 600:
        raise LinkedInPublishError(
            "LinkedIn server error",
            error_type=PublishErrorType.SERVER,
            retryable=True,
        )

    # ❌ Client errors
    if response.status_code >= 400:
        raise LinkedInPublishError(
            f"LinkedIn client error {response.status_code}: {response.text}",
            error_type=PublishErrorType.CLIENT,
            retryable=False,
        )

    data = response.json()

    if "id" not in data:
        raise LinkedInPublishError(
            f"LinkedIn response missing post ID: {data}",
            error_type=PublishErrorType.SERVER,
            retryable=True,
        )

    linkedin_urn = data["id"]

    return {
        "platform": Platform.LINKEDIN,
        "external_post_id": linkedin_urn,
        "url": f"https://www.linkedin.com/feed/update/{linkedin_urn}/",
    }
