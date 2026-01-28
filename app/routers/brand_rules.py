from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db.models.brand_rule import BrandRule
from app.schemas.brand_rule import BrandRuleCreate, BrandRuleResponse
from app.core.rule_types import ALLOWED_RULE_TYPES

print("🔥 LOADED brand_rules router")

router = APIRouter()


def get_dev_context():
    return {
        "client_id": 6,
        "brand_id": 14   # ⚠️ replace later with real auth
    }


# -------------------------
# CREATE RULE
# -------------------------
@router.post("/", response_model=BrandRuleResponse)
def create_rule(
    payload: BrandRuleCreate,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_dev_context)
):
    brand_id = ctx["brand_id"]

    rule_type = payload.rule_type.upper().strip()

    if rule_type not in ALLOWED_RULE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rule_type. Must be one of {sorted(ALLOWED_RULE_TYPES)}"
        )

    rule = BrandRule(
        brand_id=brand_id,
        platform=payload.platform,
        category_id=payload.category_id,
        rule_type=rule_type,
        rule_text=payload.rule_text,
        is_system=False
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# -------------------------
# LIST RULES (✅ THIS WAS MISSING)
# -------------------------
@router.get("/list", response_model=List[BrandRuleResponse])
def list_rules(
    platform: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_dev_context)
):
    brand_id = ctx["brand_id"]

    q = db.query(BrandRule).filter(BrandRule.brand_id == brand_id)

    if platform:
        q = q.filter(BrandRule.platform == platform)

    if category_id:
        q = q.filter(BrandRule.category_id == category_id)

    return q.all()


# -------------------------
# TOGGLE RULE
# -------------------------
@router.patch("/{rule_id}/toggle", response_model=BrandRuleResponse)
def toggle_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_dev_context)
):
    brand_id = ctx["brand_id"]

    rule = db.query(BrandRule).filter(
        BrandRule.id == rule_id,
        BrandRule.brand_id == brand_id
    ).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)
    return rule
