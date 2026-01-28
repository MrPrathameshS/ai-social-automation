from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.brand_profile import BrandProfile

# must match your auth router prefix
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "super-secret-dev-key"  # must match create_access_token
ALGORITHM = "HS256"


# =====================
# CURRENT USER
# =====================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise credentials_exception

    return user


# =====================
# CURRENT BRAND
# =====================
def get_current_brand(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BrandProfile:
    brand = (
        db.query(BrandProfile)
        .filter(BrandProfile.client_id == user.client_id)
        .first()
    )

    if not brand:
        raise HTTPException(
            status_code=404,
            detail="Brand not found for current user",
        )

    return brand
