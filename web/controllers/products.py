import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

import models
from core.security import verify_token
from schemas import ProductResponse
from core.database import SessionLocal
from helpers.utils import paginate
from services.product_service import ProductService

router = APIRouter(tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        return verify_token(auth_header.split(" ")[1])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def _check_product_permission(current_user: dict, db: Session, required_perm: str = "create"):
    if current_user.get("role") == "super_admin":
        return

    user_db = db.query(models.AdminStaff).filter(
        models.AdminStaff.id == current_user.get("user_id")
    ).first()
    if not user_db:
        raise HTTPException(status_code=403, detail="Admin staff not found")

    perms_dict = user_db.permissions if isinstance(user_db.permissions, dict) else {}
    if isinstance(user_db.permissions, str):
        try:
            perms_dict = json.loads(user_db.permissions or "{}")
        except Exception:
            pass
    products_perms = perms_dict.get("products", [])
    if isinstance(products_perms, list) and required_perm in products_perms:
        return

    if "manage_products" in str(user_db.permissions or ""):
        return

    raise HTTPException(
        status_code=403,
        detail=f"Not authorized. 'products:{required_perm}' permission required."
    )

@router.post("/add-product", response_model=ProductResponse)
def add_product(
    product_name: str = Form(...),
    product_type: str = Form(...),
    unit_price: float = Form(0.0),
    unit_mrp: float = Form(...),
    discount: float = Form(0.0),
    description: str = Form(None),
    brand: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    selling_price: Optional[float] = Form(None),
    referral_discount: float = Form(0.0),
    tax_gst: Optional[float] = Form(None),
    stock_pieces: int = Form(0),
    product_status: str = Form("Active"),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    request: Request = None,
):
    current_user = _get_current_user(request)
    _check_product_permission(current_user, db, required_perm="create")

    return ProductService.create_product(
        db=db,
        product_name=product_name,
        product_type=product_type,
        unit_mrp=unit_mrp,
        unit_price=unit_price,
        discount=discount,
        description=description,
        brand=brand,
        model_name=model_name,
        selling_price=selling_price,
        referral_discount=referral_discount,
        tax_gst=tax_gst,
        stock_pieces=stock_pieces,
        product_status=product_status,
        target_audience="patient_doctor",
        images=images if images else [],
    )

@router.put("/update-product/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_name: str = Form(...),
    product_type: str = Form(...),
    unit_price: float = Form(0.0),
    unit_mrp: float = Form(...),
    discount: float = Form(0.0),
    description: str = Form(None),
    brand: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    selling_price: Optional[float] = Form(None),
    referral_discount: float = Form(0.0),
    tax_gst: float = Form(0.0),
    stock_pieces: int = Form(0),
    product_status: str = Form("Active"),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    request: Request = None,
):
    current_user = _get_current_user(request)
    _check_product_permission(current_user, db, required_perm="edit")

    return ProductService.update_product(
        db=db,
        product_id=product_id,
        product_name=product_name,
        product_type=product_type,
        unit_mrp=unit_mrp,
        unit_price=unit_price,
        discount=discount,
        description=description,
        brand=brand,
        model_name=model_name,
        selling_price=selling_price,
        referral_discount=referral_discount,
        tax_gst=tax_gst,
        stock_pieces=stock_pieces,
        product_status=product_status,
        images=images if images else [],
    )

@router.get("/")
def get_products(
    request: Request,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(models.Product).filter(
        models.Product.is_available == True,
        models.Product.target_audience == "patient_doctor",
    )
    products = paginate(query, page=page, limit=limit)

    for product in products["data"]:
        if product.product_image:
            product.image_url = f"{request.base_url}uploads/products/{product.product_image}"
        else:
            product.image_url = None

        if product.product_images:
            try:
                images_list = json.loads(product.product_images)
                product.image_urls = [
                    f"{request.base_url}uploads/products/{img}" for img in images_list
                ]
            except Exception:
                product.image_urls = []
        else:
            product.image_urls = []

    return products

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    current_user = _get_current_user(request)

    if current_user.get("role") not in ["super_admin", "admin", "distributor"]:
        raise HTTPException(status_code=403, detail="Not authorized.")

    product = ProductService.get_product_by_id(db, product_id)

    if current_user.get("role") == "distributor" and product.distributor_id != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this product.")

    product.is_available = False
    product.product_status = "Deleted"
    db.commit()
    return {"detail": "Product deleted successfully"}
