from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import UserCreate, UserLogin, UserResponse
from auth import hash_password, verify_password, create_token
from validators import validate_email, validate_password, validate_phone, validate_pincode, validate_age, validate_role
from exception import ConflictException, NotFoundException, AuthenticationException, DatabaseException
import random
# Create router
router = APIRouter(
    tags=["Authentication"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ REGISTER
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Validate email
    validated_email = validate_email(user.email)
    
    # Check if email already exists
    if db.query(models.User).filter(models.User.email == validated_email).first():
        raise ConflictException("Email already registered. Please use a different email or login.")
    
    # Validate password
    validated_password = validate_password(user.password)
    
    # Validate phone
    validated_phone = validate_phone(user.phone)
    
    # Validate role
    validated_role = validate_role(user.role)
    
    # Validate age
    validated_age = validate_age(user.age)
    
    # Validate pincode
    validated_pincode = validate_pincode(user.pincode)
    
    # Create user
    new_user = models.User(
        name=user.name.strip(),
        email=validated_email,
        password=hash_password(validated_password),
        role=validated_role,    
        referral_code=f"{user.name[:4].upper()}{random.randint(100,999)}",
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
        company_name=user.companyName,
        business_type=user.businessType,
        distributor_type=user.distributorType,
        license_number=user.licenseNumber,
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create user: {str(e)}")

# ✅ LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Validate email
    validated_email = validate_email(user.email)
    
    # Find user
    db_user = db.query(models.User).filter(models.User.email == validated_email).first()
    if not db_user:
        raise NotFoundException("User not found. Please check your email or register.")
    
    # Verify password
    if not verify_password(user.password, db_user.password):
        raise AuthenticationException("Invalid password. Please try again.")
    
    # Create token
    token = create_token({"user_id": db_user.id, "role": db_user.role})
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role,
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "permissions": db_user.permissions
        }
    }