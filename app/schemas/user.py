from pydantic import BaseModel
from typing import Optional, Union

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
    status: Optional[str] = None
    verification_status: Optional[str] = None
    commission: Optional[float] = None
    discount: Optional[float] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    custom_id: Optional[str] = None
    name: str
    email: str
    role: str
    phone: Union[int, str]
    permissions: Optional[str] = None
    class Config:
        from_attributes = True
