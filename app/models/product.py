from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    product_type = Column(String)
    unit_price = Column(Float)
    unit_mrp = Column(Float)
    discount = Column(Float, default=0.0)
    customer_discount = Column(Float, default=0.0)
    distributor_discount = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    description = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    target_audience = Column(String, default="patient_doctor")
    created_at = Column(DateTime, default=datetime.utcnow)
    product_image = Column(String, nullable=True)
    product_images = Column(Text, nullable=True)
    brand = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    selling_price = Column(Float, nullable=True)
    referral_discount = Column(Float, default=0.0)
    tax_gst = Column(Float, default=0.0)
    stock_pieces = Column(Integer, default=0)
    product_status = Column(String, default="Active")
    distributor_id = Column(Integer, nullable=True)
