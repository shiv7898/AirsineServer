from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    product_name: str
    product_type: str
    brand: Optional[str] = None
    model_name: Optional[str] = None
    unit_price: float
    unit_mrp: float
    selling_price: Optional[float] = None
    discount: float = 0.0
    customer_discount: float = 0.0
    distributor_discount: float = 0.0
    referral_discount: float = 0.0
    tax_gst: Optional[float] = None
    stock_pieces: int = 0
    product_status: str = "Active"
    target_audience: Optional[str] = "patient_doctor"
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    product_code: Optional[str] = None
    product_name: str
    product_type: str
    brand: Optional[str] = None
    model_name: Optional[str] = None
    unit_price: float
    unit_mrp: float
    selling_price: Optional[float] = None
    discount: float
    customer_discount: float
    distributor_discount: float
    referral_discount: float
    tax_gst: float
    stock_pieces: int
    product_status: str
    target_audience: str
    currency: str
    is_available: bool
    product_image: Optional[str] = None
    product_images: Optional[str] = None
    class Config:
        from_attributes = True
