from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import verify_password, create_access_token
from app.db.models.brand_profile import BrandProfile
router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"




@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 🔹 Fetch brand for this client
    brand = db.query(BrandProfile).filter(
        BrandProfile.client_id == user.client_id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=400,
            detail="No brand found for this client"
        )

    token = create_access_token({
        "sub": user.email,          # always use email for consistency
        "client_id": user.client_id,
        "brand_id": brand.id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
