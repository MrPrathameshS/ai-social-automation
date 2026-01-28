from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Client, BrandProfile
from app.core.security import hash_password, verify_password
from app.core.security import create_access_token

from app.api.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# =====================
# REGISTER
# =====================

@router.post("/register", response_model=RegisterResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    # 1. User exists?
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # 2. Get or create client
    client = (
        db.query(Client)
        .filter(Client.company_name == request.company_name)
        .first()
    )

    if not client:
        client = Client(company_name=request.company_name)
        db.add(client)
        db.commit()
        db.refresh(client)

    # 3. Ensure exactly ONE brand per client
    brand = (
        db.query(BrandProfile)
        .filter(BrandProfile.client_id == client.id)
        .first()
    )

    if not brand:
        brand = BrandProfile(
            brand_name=request.brand_name,
            client_id=client.id,
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)

    # 4. Create user
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        client_id=client.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. Issue token (IDENTITY ONLY)
    token = create_access_token({
        "sub": str(user.id)
    })


    return RegisterResponse(access_token=token)


# =====================
# LOGIN
# =====================

@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({
        "sub": str(user.id)   # ✅ MUST be user.id
    })


    return LoginResponse(access_token=token)
