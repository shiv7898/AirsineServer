from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    referral_code: Optional[str] = None
    customer_name: str
    customer_phone: int
    building: str
    locality: str
    district: str
    state: str
    pincode: int

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_amount: float
    discount_amount: float
    final_amount: float
    status: str
    order_date: datetime

    class Config:
        from_attributes = True
