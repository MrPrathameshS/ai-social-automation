from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.services import brand_service

router = APIRouter(prefix="/brands", tags=["Brands"])
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse



# TEMP until auth is implemented
def get_current_client_id():
    return 6



@router.post("/", response_model=BrandResponse)
def create_brand(brand_data: BrandCreate, db: Session = Depends(get_db)):
    client_id = get_current_client_id()
    return brand_service.create_brand(db, client_id, brand_data)



@router.get("/", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    client_id = get_current_client_id()
    return brand_service.get_brands(db, client_id)




@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    client_id = get_current_client_id()
    brand = brand_service.get_brand_by_id(db, brand_id, client_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return brand


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(brand_id: int, brand_data: BrandUpdate, db: Session = Depends(get_db)):
    client_id = get_current_client_id()
    brand = brand_service.get_brand_by_id(db, brand_id, client_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return brand_service.update_brand(db, brand, brand_data)


@router.patch("/{brand_id}/activate", response_model=BrandResponse)
def activate_brand(brand_id: int, is_active: bool, db: Session = Depends(get_db)):
    client_id = get_current_client_id()
    brand = brand_service.get_brand_by_id(db, brand_id, client_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return brand_service.activate_brand(db, brand, is_active)


@router.delete("/{brand_id}")
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    client_id = get_current_client_id()
    brand = brand_service.get_brand_by_id(db, brand_id, client_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_service.delete_brand(db, brand)
    return {"status": "deleted"}
