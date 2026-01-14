from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.brand_profile import (
    BrandProfileCreate,
    BrandProfileUpdate,
    BrandProfileOut
)
from app.services.brand_profile_service import (
    create_brand_profile,
    get_brand_profiles,
    get_brand_profile,
    update_brand_profile,
    delete_brand_profile
)

router = APIRouter(prefix="/brand-profiles", tags=["Brand Profiles"])


@router.post("/", response_model=BrandProfileOut)
def create(data: BrandProfileCreate, db: Session = Depends(get_db)):
    return create_brand_profile(db, data)


@router.get("/", response_model=list[BrandProfileOut])
def list_all(client_id: int = None, db: Session = Depends(get_db)):
    return get_brand_profiles(db, client_id)


@router.get("/{brand_id}", response_model=BrandProfileOut)
def get_one(brand_id: int, db: Session = Depends(get_db)):
    brand = get_brand_profile(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return brand


@router.put("/{brand_id}", response_model=BrandProfileOut)
def update(brand_id: int, data: BrandProfileUpdate, db: Session = Depends(get_db)):
    brand = update_brand_profile(db, brand_id, data)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return brand


@router.delete("/{brand_id}")
def delete(brand_id: int, db: Session = Depends(get_db)):
    success = delete_brand_profile(db, brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return {"status": "deleted"}
