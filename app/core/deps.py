from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.brand_profile import BrandProfile
from app.core.security import SECRET_KEY, ALGORITHM


#security = HTTPBearer()

#def get_current_user(
#    credentials: HTTPAuthorizationCredentials = Depends(security),
#    db: Session = Depends(get_db),
#):
#    token = credentials.credentials
#
#    try:
#        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#        sub = payload.get("sub")
 #   except Exception:
#        raise HTTPException(status_code=401, detail="Invalid token")
#
    # 🔥 HARD GUARD
 #   if not sub or not sub.isdigit():
  #      raise HTTPException(
   #         status_code=status.HTTP_401_UNAUTHORIZED,
    #        detail="Invalid authentication token",
     #   )
#
 #   user = db.query(User).filter(User.id == int(sub)).first()
  #  if not user:
   #     raise HTTPException(status_code=401, detail="User not found")
#
 #   return user



security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    token = None

    # 1️⃣ Header token (normal API usage)
    if credentials:
        token = credentials.credentials

    # 2️⃣ Query param token (DEV / browser OAuth only)
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not sub or not str(sub).isdigit():
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user




def get_current_brand(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = (
        db.query(BrandProfile)
        .filter(BrandProfile.client_id == user.client_id)
        .first()
    )

    if not brand:
        raise HTTPException(
            status_code=400,
            detail="No brand found for this client",
        )

    return brand
