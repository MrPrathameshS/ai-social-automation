from fastapi import APIRouter, HTTPException
import requests
import urllib.parse
from app.core.config import settings
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

router = APIRouter()

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

LINKEDIN_TOKEN_STORE = {
    "access_token": None,
    "expires_in": None,
    "sub": None
}
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

# ---------------------------
# STEP 1: CONNECT
# ---------------------------
@router.get("/linkedin/connect")
def linkedin_connect():
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET or not settings.LINKEDIN_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="LinkedIn credentials not set")

    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "scope": "openid profile w_member_social"
    }

    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    return {"auth_url": url}


# ---------------------------
# STEP 2: CALLBACK
# ---------------------------
@router.get("/linkedin/callback")
def linkedin_callback(code: str):
    try:
        print("🔵 Received code:", code)

        session = requests.Session()
        session.mount("https://", TLSAdapter())

        token_resp = session.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )

        print("🟡 Token status:", token_resp.status_code)
        print("🟡 Token response:", token_resp.text)

        token_resp.raise_for_status()
        token_data = token_resp.json()

        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in")

        LINKEDIN_TOKEN_STORE["access_token"] = access_token
        LINKEDIN_TOKEN_STORE["expires_in"] = expires_in

        print("🟢 Access token stored")

        profile_resp = session.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )

        print("🟣 Profile status:", profile_resp.status_code)
        print("🟣 Profile response:", profile_resp.text)

        profile_resp.raise_for_status()
        profile_data = profile_resp.json()

        LINKEDIN_TOKEN_STORE["sub"] = profile_data.get("sub")

        return {
            "message": "LinkedIn connected successfully",
            "profile": profile_data
        }

    except Exception as e:
        print("🔴 CALLBACK ERROR:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# STEP 3: FETCH PROFILE
# ---------------------------
@router.get("/linkedin/me")
def linkedin_me():
    access_token = LINKEDIN_TOKEN_STORE.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")

    response = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Profile fetch failed: {response.text}"
        )

    return response.json()


# ---------------------------
# STEP 4: PUBLISH TEST POST
# ---------------------------
@router.post("/linkedin/publish-test")
def publish_test_post():
    access_token = LINKEDIN_TOKEN_STORE.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="LinkedIn not connected")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    sub = LINKEDIN_TOKEN_STORE.get("sub")

    if not sub:
        raise HTTPException(status_code=500, detail="LinkedIn user sub not found")

    author_urn = f"urn:li:person:{sub}"

    post_payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "🚀 This post was published by my AI automation system. Manual posting is officially dead."
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    post_resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        json=post_payload,
        headers=headers,
        timeout=10
    )

    print("🟠 Post status:", post_resp.status_code)
    print("🟠 Post response:", post_resp.text)

    if post_resp.status_code not in [200, 201]:
        raise HTTPException(
            status_code=500,
            detail=f"Post failed: {post_resp.text}"
        )

    return {
        "message": "Post published successfully",
        "linkedin_response": post_resp.json()
    }
