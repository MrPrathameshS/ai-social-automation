from sqlalchemy.orm import Session
from app.db.models import BrandProfile
from app.schemas.brand import BrandCreate, BrandUpdate


from app.db.models.brand_profile import BrandProfile


def create_brand(db: Session, client_id: int, brand_data: BrandCreate):
    brand = BrandProfile(
        brand_name=brand_data.brand_name,
        platform=brand_data.platform,
        tone_description=brand_data.tone_description,
        audience_description=brand_data.audience_description,
        writing_style=brand_data.writing_style,
        do_not_use=brand_data.do_not_use,
        client_id=client_id
    )

    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand






def get_brands(db, client_id: int):
    return db.query(BrandProfile).filter(BrandProfile.client_id == client_id).all()



def get_brand_by_id(db: Session, brand_id: int, client_id: int):
    return db.query(BrandProfile).filter(
        BrandProfile.id == brand_id,
        BrandProfile.client_id == client_id
    ).first()


def update_brand(db: Session, brand, brand_data: BrandUpdate):
    update_data = brand_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        brand.brand_name = update_data["name"]

    if "tone" in update_data:
        brand.tone_description = update_data["tone"]

    if "target_audience" in update_data:
        brand.audience_description = update_data["target_audience"]

    if "brand_values" in update_data:
        brand.writing_style = update_data["brand_values"]

    if "do_not_use" in update_data:
        brand.do_not_use = update_data["do_not_use"]

    if "platform_preferences" in update_data and update_data["platform_preferences"]:
        brand.platform = update_data["platform_preferences"].get("platform", brand.platform)

    if "is_active" in update_data:
        brand.is_active = update_data["is_active"]

    db.commit()
    db.refresh(brand)
    return brand


def activate_brand(db: Session, brand: BrandProfile, is_active: bool):
    brand.is_active = is_active
    db.commit()
    db.refresh(brand)
    return brand


def delete_brand(db: Session, brand: BrandProfile):
    db.delete(brand)
    db.commit()
