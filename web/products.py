from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import app.models as models
from app.schemas import ProductCreate, ProductResponse
from helpers.utils import paginate
from fastapi import Request, Form
from app.core.auth import verify_token
from fastapi import UploadFile, File
from datetime import datetime
import shutil
import os
import json
from typing import List, Optional

# Create router instance
router = APIRouter(
    tags=["Products"]     # Shows in Swagger docs
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ADD PRODUCT WITH IMAGE
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
    request: Request = None
):
    try:
        # Check authentication since this route is skipped in middleware
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            current_user = verify_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Authorization check
        if current_user.get("role") != "super_admin":
            user_db = db.query(models.AdminStaff).filter(models.AdminStaff.id == current_user.get("user_id")).first()
            if not user_db:
                raise HTTPException(status_code=403, detail="Admin staff not found")
            
            perms_str = user_db.permissions or "{}"
            has_permission = False
            
            try:
                perms_dict = json.loads(perms_str)
                products_perms = perms_dict.get("products", [])
                if isinstance(products_perms, list) and ("create" in products_perms or "edit" in products_perms):
                    has_permission = True
            except:
                pass
                
            if "create_product" in perms_str or "manage_products" in perms_str:
                has_permission = True
                
            if not has_permission:
                raise HTTPException(status_code=403, detail="Not authorized. 'products:edit' permission required.")


        image_filename = None
        image_filenames = []

        # CREATE uploads/products FOLDER
        os.makedirs("uploads/products", exist_ok=True)

        # SAVE IMAGES
        if images:
            for img in images:
                if img.filename:
                    extension = img.filename.split(".")[-1]
                    # use datetime with microsecond to avoid name collision if multiple images uploaded at same second
                    img_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{extension}"
                    image_path = f"uploads/products/{img_name}"
                    with open(image_path, "wb") as buffer:
                        shutil.copyfileobj(img.file, buffer)
                    image_filenames.append(img_name)
            
            if image_filenames:
                image_filename = image_filenames[0]
                
        # Calculate selling price if not provided
        if selling_price is None:
            selling_price = unit_mrp - (unit_mrp * discount / 100.0)
            
        # Auto-fill GST if not provided
        if tax_gst is None:
            last_product = db.query(models.Product).order_by(models.Product.id.desc()).first()
            tax_gst = last_product.tax_gst if (last_product and last_product.tax_gst is not None) else 0.0

        product_images_json = json.dumps(image_filenames) if image_filenames else None

        # SAVE PRODUCT
        new_product = models.Product(
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
            product_image=image_filename,
            product_images=product_images_json,
            target_audience="patient_doctor"
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# UPDATE PRODUCT
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
        # Check authentication since this route is skipped in middleware
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            current_user = verify_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Authorization check
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

        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        image_filenames = []
        if product.product_images:
            try:
                image_filenames = json.loads(product.product_images)
            except:
                pass

        # SAVE IMAGES if provided (Append)
        if images and len(images) > 0 and images[0].filename:
            os.makedirs("uploads/products", exist_ok=True)
            for img in images:
                if img.filename:
                    extension = img.filename.split(".")[-1]
                    img_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{extension}"
                    image_path = f"uploads/products/{img_name}"
                    with open(image_path, "wb") as buffer:
                        import shutil
                        shutil.copyfileobj(img.file, buffer)
                    image_filenames.append(img_name)
                    
        # Calculate selling price if not provided
        if selling_price is None:
            selling_price = unit_mrp - (unit_mrp * discount / 100.0)

        product_images_json = json.dumps(image_filenames) if image_filenames else None
        image_filename = image_filenames[0] if image_filenames else None

        # UPDATE PRODUCT
        product.product_name = product_name
        product.product_type = product_type
        product.unit_price = unit_price
        product.unit_mrp = unit_mrp
        product.discount = discount
        product.description = description
        product.brand = brand
        product.model_name = model_name
        product.selling_price = selling_price
        product.referral_discount = referral_discount
        product.tax_gst = tax_gst if tax_gst is not None else product.tax_gst
        product.stock_pieces = stock_pieces
        product.product_status = product_status
        product.product_images = product_images_json
        if image_filename:
            product.product_image = image_filename

        db.commit()
        db.refresh(product)

        return product

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# GET ALL PRODUCTS (With Pagination + Images)
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

    # ADD IMAGE URL
    for product in products["data"]:

        if product.product_image:
            product.image_url = (
                f"{request.base_url}uploads/products/{product.product_image}"
            )
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

# DELETE PRODUCT
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
            
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if current_user.get("role") == "distributor" and product.distributor_id != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to delete this product.")

        product.is_available = False
        product.product_status = "Deleted"
        db.commit()
        return {"detail": "Product deleted successfully"}

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
