from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    product_id = Column(Integer, ForeignKey("products.id"))
    customer_name = Column(String)
    customer_phone = Column(String)
    quantity = Column(Integer, default=1)
    total_amount = Column(Float)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, default=0)
    currency = Column(String, default="INR")
    status = Column(Integer, default=0)
    referral_code = Column(String, nullable=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    building = Column(String)
    locality = Column(String)
    district = Column(String)
    state = Column(String)
    pincode = Column(String)
