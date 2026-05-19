from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import ProductCreate, ProductResponse
from utils import paginate
from fastapi import Request
from fastapi import UploadFile, File
from datetime import datetime
import shutil
import os

# Create router instance
router = APIRouter(
    prefix="/products",  # All routes will start with /products
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
    product_name: str,
    product_type: str,
    unit_price: float,
    unit_mrp: float,
    discount: float,
    description: str = None,
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:

        image_filename = None

        # CREATE uploads/products FOLDER
        os.makedirs("uploads/products", exist_ok=True)

        # SAVE IMAGE
        if image:
            extension = image.filename.split(".")[-1]

            image_filename = (
                f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{extension}"
            )

            image_path = f"uploads/products/{image_filename}"

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        # SAVE PRODUCT
        new_product = models.Product(
            product_name=product_name,
            product_type=product_type,
            unit_price=unit_price,
            unit_mrp=unit_mrp,
            discount=discount,
            description=description,
            product_image=image_filename
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

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
        models.Product.is_available == True
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

    return products