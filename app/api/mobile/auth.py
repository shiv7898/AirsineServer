from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import app.models as models
from app.schemas import UserCreate, UserLogin, UserResponse
from app.core.auth import hash_password, verify_password, create_token
from helpers.validators import validate_email, validate_password, validate_phone, validate_pincode, validate_age, validate_role
from app.core.exception import ConflictException, NotFoundException, AuthenticationException, DatabaseException
import random
from web.admin import generate_custom_id_for_db

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

# Helper to check if email is taken across all tables
def is_email_taken(db: Session, email: str) -> bool:
    email_lower = email.lower().strip()
    if db.query(models.User).filter(models.User.email == email_lower).first():
        return True
    if db.query(models.Distributor).filter(models.Distributor.email == email_lower).first():
        return True
    if db.query(models.AdminStaff).filter(models.AdminStaff.email == email_lower).first():
        return True
    if db.query(models.SuperAdmin).filter(models.SuperAdmin.email == email_lower).first():
        return True
    return False

# Helper to find user by email across all tables
def find_user_by_email(db: Session, email: str):
    email_lower = email.lower().strip()
    user = db.query(models.User).filter(models.User.email == email_lower).first()
    if user:
        return user
    distributor = db.query(models.Distributor).filter(models.Distributor.email == email_lower).first()
    if distributor:
        return distributor
    admin_staff = db.query(models.AdminStaff).filter(models.AdminStaff.email == email_lower).first()
    if admin_staff:
        return admin_staff
    super_admin = db.query(models.SuperAdmin).filter(models.SuperAdmin.email == email_lower).first()
    if super_admin:
        return super_admin
    return None

# ✅ REGISTER
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Validate email
    validated_email = validate_email(user.email)
    
    # Check if email already exists
    if is_email_taken(db, validated_email):
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
    
    # Generate custom ID based on role
    custom_id = generate_custom_id_for_db(db, validated_role)
    
    # Create user depending on role
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
    else:  # patient, doctor
        new_user = models.User(
            custom_id=custom_id,
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
    db_user = find_user_by_email(db, validated_email)
    if not db_user:
        raise NotFoundException("User not found. Please check your email or register.")
        
    # Enforce role-based panel separation (Mobile login restricts to doctors, patients, distributors)
    if db_user.role in ["super_admin", "admin", "sub_admin"]:
        raise AuthenticationException("Access denied. Administrative accounts cannot log in to the mobile application.")
        
    # Check if admin/subadmin is inactive or blocked
    if db_user.role in ["admin", "sub_admin"] and db_user.status and db_user.status.lower() in ["inactive", "blocked"]:
        raise HTTPException(status_code=403, detail="Account Access Suspended. Your account is currently inactive. Please contact the Airsine administration or your superior for further assistance.")
    
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
            "pincode": db_user.pincode
        }
    }