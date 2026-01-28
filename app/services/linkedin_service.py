import requests
from app.core.config import settings

LINKEDIN_UGC_POST_URL = "https://api.linkedin.com/v2/ugcPosts"


def publish_to_linkedin(content_text: str):
    """
    Publishes a text-only post to LinkedIn using w_member_social.
    """

    payload = {
        "author": "urn:li:person:me",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401"
    }

    response = requests.post(
        LINKEDIN_UGC_POST_URL,
        json=payload,
        headers=headers,
        timeout=10
    )

    if response.status_code not in (200, 201):
        raise Exception(
            f"LinkedIn publish failed: {response.status_code} {response.text}"
        )

    return response.json()
