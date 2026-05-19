from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    phone = Column(String)
    gender = Column(String)
    age = Column(Integer)
    dob = Column(String)
    home_address = Column(String)
    area = Column(String)
    district = Column(String)
    state = Column(String)
    pincode = Column(String)
    hospital = Column(String, nullable=True)
    specialisation = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    distributor_type = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    referral_code = Column(String, unique=True, nullable=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    product_type = Column(String)
    unit_price = Column(Float)
    unit_mrp = Column(Float)
    discount = Column(Float)
    currency = Column(String, default="INR")
    description = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    product_image = Column(String, nullable=True)
    distributor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
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

class ReferralCode(Base):
    __tablename__ = "referral_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    role = Column(String)
    discount_percent = Column(Float)
    used_count = Column(Integer, default=0)  # ← ADD THIS LINE
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TherapyData(Base):
    __tablename__ = "therapy_data"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    compliance = Column(Float, nullable=True)
    usage_time = Column(Float, nullable=True)
    ahi_index = Column(Float, nullable=True)
    avg_pressure = Column(Float, nullable=True)
    leak_rate = Column(Float, nullable=True)
    duration_type = Column(String, nullable=True)
    pdf_filename = Column(String, nullable=True)

class MachineSettings(Base):
    __tablename__ = "machine_settings"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    therapy_mode = Column(String, default="Auto CPAP")
    min_pressure = Column(Float, default=4.0)
    max_pressure = Column(Float, default=15.0)
    start_pressure = Column(Float, default=4.0)
    ramp_duration = Column(Integer, default=20)
    pressure_off = Column(Float, default=2.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    image = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PdfReportData(Base):
    __tablename__ = "pdf_report_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    app_user_name = Column(String, nullable=True)
    app_user_email = Column(String, nullable=True)
    patient_details = Column(Text, nullable=True) # JSON string of patient form details
    total_days = Column(Integer, nullable=True)
    clinical_logs = Column(Text, nullable=True) # JSON string of full logs array
    created_at = Column(DateTime, default=datetime.utcnow)