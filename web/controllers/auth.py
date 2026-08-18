from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from core.database import SessionLocal
import models
from schemas import UserCreate, UserLogin, UserResponse
from core.security import hash_password, verify_password, create_token
from helpers.validators import (
    validate_email, validate_password, validate_phone,
    validate_pincode, validate_age, validate_role,
)
from core.exceptions import (
    ConflictException, NotFoundException, AuthenticationException, DatabaseException
)
from services.user_service import UserService

router = APIRouter(tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    validated_email = validate_email(user.email)
    
    if UserService.is_email_taken(db, validated_email):
        raise ConflictException("Email already registered. Please use a different email or login.")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_role = validate_role(user.role)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
    custom_id = UserService.generate_custom_id(db, validated_role)
    
    if validated_role == "distributor":
        new_user = models.Distributor(
            custom_id=custom_id,
            name=user.name.strip(),
            email=validated_email,
            password=hash_password(validated_password),
            role=validated_role,    
            phone=validated_phone,
            gender=user.gender,
            age=validated_age,
            dob=user.dob,
            home_address=user.homeAddress,
            area=user.area,
            district=user.district,
            state=user.state,
            pincode=validated_pincode,
            company_name=user.companyName,
            business_type=user.businessType,
            distributor_type=user.distributorType,
            license_number=user.licenseNumber,
            referral_code=UserService.generate_unique_referral_code(db),
        )
    elif validated_role == "super_admin":
        new_user = models.SuperAdmin(
            custom_id=custom_id,
            name=user.name.strip(),
            email=validated_email,
            password=hash_password(validated_password),
            role=validated_role,    
            phone=validated_phone,
            gender=user.gender,
            age=validated_age,
            dob=user.dob,
            home_address=user.homeAddress,
            area=user.area,
            district=user.district,
            state=user.state,
            pincode=validated_pincode,
        )
    elif validated_role in ["admin", "sub_admin"]:
        new_user = models.AdminStaff(
            custom_id=custom_id,
            name=user.name.strip(),
            email=validated_email,
            password=hash_password(validated_password),
            role=validated_role,    
            phone=validated_phone,
            gender=user.gender,
            age=validated_age,
            dob=user.dob,
            home_address=user.homeAddress,
            area=user.area,
            district=user.district,
            state=user.state,
            pincode=validated_pincode,
            permissions=user.permissions,
        )
    elif validated_role == "doctor":
        new_user = models.Doctor(
            custom_id=custom_id,
            name=user.name.strip(),
            email=validated_email,
            password=hash_password(validated_password),
            role=validated_role,    
            referral_code=UserService.generate_unique_referral_code(db),
            phone=validated_phone,
            gender=user.gender,
            age=validated_age,
            dob=user.dob,
            home_address=user.homeAddress,
            area=user.area,
            district=user.district,
            state=user.state,
            pincode=validated_pincode,
            hospital=user.hospital,
            specialisation=user.specialisation,
            qualification=user.qualification,
            experience=user.experience,
        )
    else:  # patient
        new_user = models.Patient(
            custom_id=custom_id,
            name=user.name.strip(),
            email=validated_email,
            password=hash_password(validated_password),
            role=validated_role,    
            phone=validated_phone,
            gender=user.gender,
            age=validated_age,
            dob=user.dob,
            home_address=user.homeAddress,
            area=user.area,
            district=user.district,
            state=user.state,
            pincode=validated_pincode,
            referral_code=UserService.generate_unique_referral_code(db),
        )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create user: {str(e)}")

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    email_input = user.email.lower().strip()
    
    db_user = UserService.find_user_by_email(db, email_input)
    if not db_user:
        raise NotFoundException("User not found. Please check your email or register.")
        
    if db_user.role not in ["super_admin", "admin", "sub_admin"]:
        raise AuthenticationException("Access denied. Doctor, Patient, and Distributor roles cannot log in from the web panel.")
        
    if db_user.role in ["admin", "sub_admin"] and db_user.status and db_user.status.lower() in ["inactive", "blocked"]:
        raise HTTPException(status_code=403, detail="Account Access Suspended. Your account is currently inactive. Please contact the Airsine administration or your superior for further assistance.")
    
    if not verify_password(user.password, db_user.password):
        raise AuthenticationException("Invalid password. Please try again.")
    
    token = create_token({"user_id": db_user.id, "role": db_user.role})
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role,
        "user": {
            "id": db_user.id,
            "custom_id": db_user.custom_id,
            "name": db_user.name,
            "email": db_user.email,
            "permissions": getattr(db_user, 'permissions', None),
            "phone": db_user.phone,
            "gender": db_user.gender,
            "age": db_user.age,
            "dob": db_user.dob,
            "homeAddress": db_user.home_address,
            "area": db_user.area,
            "district": db_user.district,
            "state": db_user.state,
            "pincode": db_user.pincode,
            "referral_code": getattr(db_user, 'referral_code', None)
        }
    }
