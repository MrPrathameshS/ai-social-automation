import requests
import os
from requests.exceptions import RequestException
from app.services.linkedin.errors import LinkedInAuthError


class LinkedInAPIError(Exception):
    def __init__(self, status_code: int, payload: dict | str):
        self.status_code = status_code
        self.payload = payload
        super().__init__(str(payload))


class LinkedInClient:
    BASE_URL = "https://api.linkedin.com/v2"  # dev-only

    def __init__(self, access_token: str):
        self.access_token = access_token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def create_text_post(self, author_urn: str, text: str) -> str:
        # 🔴 DEV-ONLY: force retryable failure
        if os.getenv("LINKEDIN_FORCE_500") == "1":
            raise LinkedInAPIError(
                status_code=500,
                payload="Simulated LinkedIn 500 for retry test",
            )

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        try:
            res = requests.post(
                f"{self.BASE_URL}/ugcPosts",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
        except RequestException as e:
            raise LinkedInAPIError(
                status_code=503,
                payload=f"Network error: {str(e)}",
            )

        if res.status_code in (401, 403):
            raise LinkedInAuthError("LinkedIn authorization expired")

        if res.status_code >= 400:
            raise LinkedInAPIError(res.status_code, res.text)


        post_urn = res.json().get("id")
        if not post_urn:
            raise LinkedInAPIError(500, res.json())

        return post_urn
