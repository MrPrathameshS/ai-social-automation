from sqlalchemy.orm import Session
from app.db.models.brand_profile import BrandProfile
from app.schemas.brand_profile import BrandProfileCreate, BrandProfileUpdate


def create_brand_profile(db: Session, data: BrandProfileCreate):
    brand = BrandProfile(**data.dict())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def get_brand_profiles(db: Session, client_id: int = None):
    query = db.query(BrandProfile)
    if client_id:
        query = query.filter(BrandProfile.client_id == client_id)
    return query.all()


def get_brand_profile(db: Session, brand_id: int):
    return db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()


def update_brand_profile(db: Session, brand_id: int, data: BrandProfileUpdate):
    brand = get_brand_profile(db, brand_id)
    if not brand:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)
    return brand


def delete_brand_profile(db: Session, brand_id: int):
    brand = get_brand_profile(db, brand_id)
    if not brand:
        return None
    db.delete(brand)
    db.commit()
    return True
