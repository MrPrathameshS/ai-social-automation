from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import BrandProfile


def get_brand_profile_by_id(brand_id: int) -> BrandProfile:
    db: Session = SessionLocal()
    try:
        return db.query(BrandProfile).filter(
            BrandProfile.id == brand_id
        ).first()
    finally:
        db.close()


def get_brand_profile_by_name(brand_name: str) -> BrandProfile:
    db: Session = SessionLocal()
    try:
        return db.query(BrandProfile).filter(
            BrandProfile.brand_name.ilike(brand_name)
        ).first()
    finally:
        db.close()


def seed_brand_profile(
    brand_name: str,
    tone: str,
    audience: str,
    style: str,
    constraints: str
):
    db: Session = SessionLocal()
    try:
        existing = db.query(BrandProfile).filter(
            BrandProfile.brand_name.ilike(brand_name)
        ).first()

        if existing:
            print(f"⚠️ Brand profile already exists: {brand_name}")
            return

        profile = BrandProfile(
            brand_name=brand_name,
            tone_description=tone,
            audience_description=audience,
            writing_style=style,
            do_not_use=constraints,
            learned_insights=""
        )

        db.add(profile)
        db.commit()
        print(f"🌱 Seeded brand profile: {brand_name}")

    finally:
        db.close()
