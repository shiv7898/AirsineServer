"""
services/product_service.py

Centralized product business logic.
Both Web API (web/products.py) and Mobile API (app/api/mobile/)
should call these methods instead of duplicating DB logic.
"""
import json
import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

import models


class ProductService:

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_product_code(product_type: str, product_id: int) -> str:
        """Generate standard AIR-TYPE-XXXX product code."""
        type_str = product_type.upper().replace(" ", "") if product_type else "PROD"
        return f"AIR-{type_str}-{product_id:04d}"

    @staticmethod
    def _save_images(images: List[UploadFile], upload_dir: str = "uploads/products") -> List[str]:
        """Save uploaded images to disk, return list of saved filenames."""
        os.makedirs(upload_dir, exist_ok=True)
        saved_filenames = []
        for img in images:
            if img and img.filename:
                ext = img.filename.rsplit(".", 1)[-1]
                filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{ext}"
                path = os.path.join(upload_dir, filename)
                with open(path, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                saved_filenames.append(filename)
        return saved_filenames

    # ------------------------------------------------------------------
    # CREATE PRODUCT
    # ------------------------------------------------------------------

    @staticmethod
    def create_product(
        db: Session,
        product_name: str,
        product_type: str,
        unit_mrp: float,
        unit_price: float = 0.0,
        discount: float = 0.0,
        description: Optional[str] = None,
        brand: Optional[str] = None,
        model_name: Optional[str] = None,
        selling_price: Optional[float] = None,
        referral_discount: float = 0.0,
        tax_gst: Optional[float] = None,
        stock_pieces: int = 0,
        product_status: str = "Active",
        target_audience: str = "patient_doctor",
        images: Optional[List[UploadFile]] = None,
        distributor_id: Optional[int] = None,
    ) -> models.Product:
        """Create a new product, save images, auto-generate product_code."""

        # Save images
        image_filenames = []
        if images:
            image_filenames = ProductService._save_images(images)

        image_filename = image_filenames[0] if image_filenames else None
        product_images_json = json.dumps(image_filenames) if image_filenames else None

        # Auto-calculate selling price if not provided
        if selling_price is None:
            selling_price = unit_mrp - (unit_mrp * discount / 100.0)

        # Inherit last GST if not provided
        if tax_gst is None:
            last_product = db.query(models.Product).order_by(models.Product.id.desc()).first()
            tax_gst = (last_product.tax_gst if last_product and last_product.tax_gst is not None else 0.0)

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
            target_audience=target_audience,
            distributor_id=distributor_id,
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        # Auto-generate and save product_code
        new_product.product_code = ProductService._generate_product_code(
            new_product.product_type, new_product.id
        )
        db.commit()
        db.refresh(new_product)

        return new_product

    # ------------------------------------------------------------------
    # UPDATE PRODUCT
    # ------------------------------------------------------------------

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product_name: str,
        product_type: str,
        unit_mrp: float,
        unit_price: float = 0.0,
        discount: float = 0.0,
        description: Optional[str] = None,
        brand: Optional[str] = None,
        model_name: Optional[str] = None,
        selling_price: Optional[float] = None,
        referral_discount: float = 0.0,
        tax_gst: float = 0.0,
        stock_pieces: int = 0,
        product_status: str = "Active",
        images: Optional[List[UploadFile]] = None,
    ) -> models.Product:
        """Update an existing product by ID."""
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.product_name = product_name
        product.product_type = product_type
        product.unit_price = unit_price
        product.unit_mrp = unit_mrp
        product.discount = discount
        product.description = description
        product.brand = brand
        product.model_name = model_name
        product.referral_discount = referral_discount
        product.tax_gst = tax_gst
        product.stock_pieces = stock_pieces
        product.product_status = product_status

        if selling_price is not None:
            product.selling_price = selling_price
        else:
            product.selling_price = unit_mrp - (unit_mrp * discount / 100.0)

        if images:
            new_filenames = ProductService._save_images(images)
            if new_filenames:
                product.product_image = new_filenames[0]
                product.product_images = json.dumps(new_filenames)

        db.commit()
        db.refresh(product)
        return product

    # ------------------------------------------------------------------
    # DELETE PRODUCT
    # ------------------------------------------------------------------

    @staticmethod
    def delete_product(db: Session, product_id: int) -> dict:
        """Delete a product by ID."""
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}

    # ------------------------------------------------------------------
    # GET PRODUCTS
    # ------------------------------------------------------------------

    @staticmethod
    def get_products(
        db: Session,
        target_audience: Optional[str] = None,
        distributor_id: Optional[int] = None,
    ) -> List[models.Product]:
        """Fetch products, optionally filtered by audience or distributor."""
        query = db.query(models.Product)
        if target_audience:
            query = query.filter(models.Product.target_audience == target_audience)
        if distributor_id is not None:
            query = query.filter(models.Product.distributor_id == distributor_id)
        return query.order_by(models.Product.id.desc()).all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> models.Product:
        """Fetch a single product by ID."""
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
