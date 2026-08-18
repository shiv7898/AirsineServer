from fastapi import APIRouter, Depends, HTTPException, Query, Request, Form, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os
import json
from typing import List, Optional

from core.database import SessionLocal
import models
from schemas import ProductCreate, ProductResponse
from helpers.utils import paginate
from core.security import verify_token
from services.product_service import ProductService

router = APIRouter(tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    tax_gst: Optional[float] = Form(None),
    stock_pieces: int = Form(0),
    product_status: str = Form("Active"),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            current_user = verify_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        if current_user.get("role") != "super_admin":
            user_db = db.query(models.AdminStaff).filter(models.AdminStaff.id == current_user.get("user_id")).first()
            if not user_db:
                raise HTTPException(status_code=403, detail="Admin staff not found")
            
            perms_str = user_db.permissions or "{}"
            has_permission = False
            
            try:
                perms_dict = json.loads(perms_str)
                products_perms = perms_dict.get("products", [])
                if isinstance(products_perms, list) and ("edit" in products_perms):
                    has_permission = True
            except:
                pass
                
            if "manage_products" in perms_str:
                has_permission = True
                
            if not has_permission:
                raise HTTPException(status_code=403, detail="Not authorized. 'products:edit' permission required.")

        if tax_gst is None:
            last_product = db.query(models.Product).order_by(models.Product.id.desc()).first()
            tax_gst = last_product.tax_gst if (last_product and last_product.tax_gst is not None) else 0.0
            
        return ProductService.update_product(
            db=db,
            product_id=product_id,
            product_name=product_name,
            product_type=product_type,
            unit_price=unit_price,
            unit_mrp=unit_mrp,
            discount=discount,
            description=description,
            brand=brand,
            model_name=model_name,
            selling_price=selling_price,
            referral_discount=referral_discount,
            tax_gst=tax_gst,
            stock_pieces=stock_pieces,
            product_status=product_status,
            images=images
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_products(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(
        models.Product.is_available == True,
        models.Product.target_audience == "patient_doctor"
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
                product.image_urls = [f"{request.base_url}uploads/products/{img}" for img in images_list]
            except:
                product.image_urls = []
        else:
            product.image_urls = []

    return products

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            current_user = verify_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        if current_user.get("role") not in ["super_admin", "admin", "distributor"]:
            raise HTTPException(status_code=403, detail="Not authorized.")
            
        ProductService.delete_product(db, product_id)
        return {"detail": "Product deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
