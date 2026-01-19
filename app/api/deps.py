from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
import jwt
from app.core.config import settings

security = HTTPBearer()

def get_current_context(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        user_email = payload.get("sub")
        client_id = payload.get("client_id")
        brand_id = payload.get("brand_id")

        if not user_email or not client_id or not brand_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return {
            "email": user_email,
            "client_id": client_id,
            "brand_id": brand_id
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
