from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    phone: Union[int, str]
    gender: str
    age: Union[int, str]
    dob: str
    homeAddress: str
    area: str
    district: str
    state: str
    pincode: Union[int, str]
    hospital: Optional[str] = None
    specialisation: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[Union[int, float, str]] = None
    companyName: Optional[str] = None
    businessType: Optional[str] = None
    distributorType: Optional[str] = None
    licenseNumber: Optional[Union[int, float, str]] = None
    permissions: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[Union[int, str]] = None
    gender: Optional[str] = None
    age: Optional[Union[int, str]] = None
    dob: Optional[str] = None
    homeAddress: Optional[str] = None
    area: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[Union[int, str]] = None
    hospital: Optional[str] = None
    specialisation: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[Union[int, float, str]] = None
    companyName: Optional[str] = None
    businessType: Optional[str] = None
    distributorType: Optional[str] = None
    licenseNumber: Optional[Union[int, float, str]] = None
    permissions: Optional[str] = None
class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: Union[int, str]
    permissions: Optional[str] = None
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    product_name: str
    product_type: str
    unit_price: float
    unit_mrp: float
    discount: float = 0.0
    customer_discount: float = 0.0
    distributor_discount: float = 0.0
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    product_name: str
    product_type: str
    unit_price: float
    unit_mrp: float
    discount: float
    customer_discount: float
    distributor_discount: float
    currency: str
    is_available: bool
    product_image: Optional[str] = None
    class Config:
        from_attributes = True

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

class ReferralCreate(BaseModel):
    code: str
    role: str
    discount_percent: float

class TherapyCreate(BaseModel):
    compliance: Optional[float] = None
    usage_time: Optional[float] = None
    ahi_index: Optional[float] = None
    avg_pressure: Optional[float] = None
    leak_rate: Optional[float] = None
    duration_type: Optional[str] = None

class MachineSettingsCreate(BaseModel):
    patient_id: int
    therapy_mode: str = "Auto CPAP"
    min_pressure: float = 4.0
    max_pressure: float = 15.0
    start_pressure: float = 4.0
    ramp_duration: int = 20
    pressure_off: float = 2.0

class SupportQueryCreate(BaseModel):
    category: str
    message: str

class SupportQueryResponse(BaseModel):
    id: int
    user_id: int
    query_type: str
    message: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True