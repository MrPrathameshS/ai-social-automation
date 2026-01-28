from sqlalchemy.orm import Session
from app.db.models.brand_rule import BrandRule


def get_active_rules(db: Session, brand_id: int, platform: str, category_id: int | None = None):
    """
    Fetch active rules for:
    - brand
    - matching platform OR global
    - matching category OR global
    """
    q = db.query(BrandRule).filter(
        BrandRule.brand_id == brand_id,
        BrandRule.is_active == True
    )

    # platform specific or global
    q = q.filter(
        (BrandRule.platform == platform) | (BrandRule.platform == None)
    )

    # category specific or global
    if category_id:
        q = q.filter(
            (BrandRule.category_id == category_id) | (BrandRule.category_id == None)
        )
    else:
        q = q.filter(BrandRule.category_id == None)

    return q.all()
