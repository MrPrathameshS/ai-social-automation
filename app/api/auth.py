from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db


from app.core.security import hash_password, create_access_token
from app.db.models import User, Client, BrandProfile

from app.core.security import verify_password
from app.api.schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse

router = APIRouter(tags=["auth"])



@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Get or create Client
    client = db.query(Client).filter(Client.company_name == request.company_name).first()
    if not client:
        client = Client(company_name=request.company_name)
        db.add(client)
        db.commit()
        db.refresh(client)

    # 3. Check if Brand already exists for this client (1:1 enforcement)
    brand = db.query(BrandProfile).filter(
        BrandProfile.client_id == client.id
    ).first()

    if not brand:
        brand = BrandProfile(
            brand_name=request.brand_name,
            client_id=client.id
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)

    # 4. Create User
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        client_id=client.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. Create token
    token = create_access_token({"sub": user.email})

    return RegisterResponse(access_token=token)




from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    brand = db.query(BrandProfile).filter(
        BrandProfile.client_id == user.client_id
    ).first()

    token = create_access_token({
        "sub": str(user.id),
        "client_id": user.client_id,
        "brand_id": brand.id if brand else None
    })

    return LoginResponse(access_token=token)



