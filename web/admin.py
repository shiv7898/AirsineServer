import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import app.models as models
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.core.auth import hash_password, create_token
from helpers.validators import validate_email, validate_password, validate_phone, validate_pincode, validate_age, validate_role, to_numeric_or_string
from app.core.exception import ConflictException, AuthorizationException, NotFoundException, DatabaseException
from typing import Optional

# Create router
router = APIRouter(
    tags=["Admin"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Permission check helper
def check_admin_permission(request: Request, required_role: str = "sub_admin"):
    """
    Check if user has admin permissions
    required_role: 'sub_admin', 'admin', or 'super_admin'
    """
    current_user = request.state.user
    
    if required_role == "super_admin":
        if current_user["role"] != "super_admin":
            raise AuthorizationException("Only Super Admin can perform this action")
    else:  # admin, sub_admin or super_admin allowed
        if current_user["role"] not in ["admin", "sub_admin", "super_admin"]:
            raise AuthorizationException("Admin access required")
    
    return current_user

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

# Helper to check if email is taken by another user during edit
def is_email_taken_by_other(db: Session, email: str, exclude_user_id: int, exclude_role: str) -> bool:
    email_lower = email.lower().strip()
    
    # Check Users table
    user = db.query(models.User).filter(models.User.email == email_lower).first()
    if user and not (exclude_role in ["patient", "doctor"] and user.id == exclude_user_id):
        return True
        
    # Check Distributors table
    dist = db.query(models.Distributor).filter(models.Distributor.email == email_lower).first()
    if dist and not (exclude_role == "distributor" and dist.id == exclude_user_id):
        return True
        
    # Check AdminStaff table
    staff = db.query(models.AdminStaff).filter(models.AdminStaff.email == email_lower).first()
    if staff and not (exclude_role in ["admin", "sub_admin"] and staff.id == exclude_user_id):
        return True
        
    # Check SuperAdmin table
    sp = db.query(models.SuperAdmin).filter(models.SuperAdmin.email == email_lower).first()
    if sp and not (exclude_role == "super_admin" and sp.id == exclude_user_id):
        return True
        
    return False

# CREATE SUPER ADMIN (Protected with secret key)
@router.post("/create-super-admin", response_model=UserResponse)
def create_super_admin(
    user: UserCreate,
    secret_key: str = Query(..., description="Secret key to create super admin"),
    db: Session = Depends(get_db)
):
    """
    Create the first super admin (Protected with secret key)
    Only works once and requires secret key
    """
    # CHECK SECRET KEY FIRST
    SUPER_ADMIN_SECRET = "AIRSINE_HOSPITAL_2026_SECRET"
    
    if secret_key != SUPER_ADMIN_SECRET:
        raise AuthorizationException("Invalid secret key! Unauthorized access.")
    
    # Check if super admin already exists
    existing_super_admin = db.query(models.SuperAdmin).filter(
        models.SuperAdmin.role == "super_admin"
    ).first()
    
    if existing_super_admin:
        raise ConflictException("Super Admin already exists! Contact system administrator.")
    
    # Validate
    validated_email = validate_email(user.email)
    if is_email_taken(db, validated_email):
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
    # Create super admin
    new_admin = models.SuperAdmin(
        name=user.name.strip(),
        email=validated_email,
        password=hash_password(validated_password),
        role="super_admin",
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
    
    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        return new_admin
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create super admin: {str(e)}")

# # CREATE SUB ADMIN (Only Super Admin can do this)
# @router.post("/create-sub-admin", response_model=UserResponse)
# def create_sub_admin(user: UserCreate, request: Request, db: Session = Depends(get_db)):
#     """
#     Create a sub-admin (Only Super Admin can do this)
#     """
#     # Check permission
#     check_admin_permission(request, required_role="super_admin")
    
#     # Validate
#     validated_email = validate_email(user.email)
#     if is_email_taken(db, validated_email):
#         raise ConflictException("Email already registered")
    
#     validated_password = validate_password(user.password)
#     validated_phone = validate_phone(user.phone)
#     validated_age = validate_age(user.age)
#     validated_pincode = validate_pincode(user.pincode)
    
#     # Create sub admin
#     new_sub_admin = models.AdminStaff(
#         name=user.name.strip(),
#         email=validated_email,
#         password=hash_password(validated_password),
#         role="sub_admin",  # Force sub_admin role
#         phone=validated_phone,
#         gender=user.gender,
#         age=validated_age,
#         dob=user.dob,
#         home_address=user.homeAddress,
#         area=user.area,
#         district=user.district,
#         state=user.state,
#         pincode=validated_pincode,
#         permissions=user.permissions,
#     )
    
#     try:
#         db.add(new_sub_admin)
#         db.commit()
#         db.refresh(new_sub_admin)
#         return new_sub_admin
#     except Exception as e:
#         db.rollback()
#         raise DatabaseException(f"Failed to create sub admin: {str(e)}")

# CREATE STAFF (Admin or Sub Admin - Only Super Admin can do this)
@router.post("/create-staff", response_model=UserResponse)
def create_staff(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a staff member (Admin or Sub Admin) - Only Super Admin can do this
    """
    # Check permission
    check_admin_permission(request, required_role="super_admin")
    
    # Validate role - only admin or sub_admin allowed for staff creation
    validated_role = validate_role(user.role)
    if validated_role not in ["admin", "sub_admin"]:
        raise HTTPException(status_code=400, detail="Invalid staff role. Must be 'admin' or 'sub_admin'")
        
    # Validate email
    validated_email = validate_email(user.email)
    if is_email_taken(db, validated_email):
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
    # Create staff
    new_staff = models.AdminStaff(
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
    
    try:
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        # Generate and assign custom_id after we have the DB id
        new_staff.custom_id = generate_custom_id_for_db(db, validated_role)
        db.commit()
        db.refresh(new_staff)
        return new_staff
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create staff member: {str(e)}")

def generate_custom_id_for_db(db: Session, role: str) -> str:
    prefix_map = {
        "patient":     "AIR-P",
        "doctor":      "AIR-DR",
        "distributor": "AIR-DI",
        "admin":       "AIR-A",
        "super_admin": "AIR-SA",
        "sub_admin":   "AIR-SBA",
    }
    prefix = prefix_map.get(role, "AIR-U")

    # Select correct model
    if role == "distributor":
        model = models.Distributor
    elif role == "super_admin":
        model = models.SuperAdmin
    elif role in ["admin", "sub_admin"]:
        model = models.AdminStaff
    else:
        model = models.User

    users = db.query(model).filter(
        model.role == role,
        model.custom_id.isnot(None)
    ).all()

    max_num = 0
    for u in users:
        if u.custom_id and u.custom_id.startswith(prefix):
            try:
                num = int(u.custom_id[len(prefix):])
                if num > max_num:
                    max_num = num
            except (ValueError, IndexError):
                pass

    return f"{prefix}{max_num + 1:03d}"

# CREATE STANDARD USER (Patient, Doctor, Distributor)
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a standard user (patient, doctor, distributor) from admin panel
    """
    # Check permission
    check_admin_permission(request, required_role="sub_admin")
    
    # Validate role
    validated_role = validate_role(user.role)
    if validated_role not in ["patient", "doctor", "distributor"]:
        raise HTTPException(status_code=400, detail="Role must be 'patient', 'doctor', or 'distributor'")
        
    # Validate email
    validated_email = validate_email(user.email)
    if is_email_taken(db, validated_email):
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
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
            license_number=str(user.licenseNumber) if user.licenseNumber else None,
            status="Active",
            verification_status="Verified"  # Admin created so verified
        )
    else:  # patient, doctor
        # Generate a unique referral code (e.g., "JOHN482")
        base = user.name.strip()[:4].upper()
        for _ in range(10):  # retry up to 10 times to avoid collision
            candidate = f"{base}{random.randint(100, 999)}"
            if not db.query(models.User).filter(models.User.referral_code == candidate).first():
                referral_code = candidate
                break
        else:
            # Fallback with larger range if all 10 attempts collide
            referral_code = f"{base}{random.randint(1000, 9999)}"

        new_user = models.User(
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
            hospital=user.hospital,
            specialisation=user.specialisation,
            qualification=user.qualification,
            experience=user.experience,
            referral_code=referral_code,
            status="Active",
            verification_status="Verified"  # Admin created so verified
        )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create user: {str(e)}")

# ADMIN DASHBOARD
@router.get("/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Get admin dashboard statistics
    """
    check_admin_permission(request, required_role="sub_admin")
    
    # Count users by role across three separate tables
    total_patients = db.query(models.User).filter(models.User.role == "patient").count()
    total_doctors = db.query(models.User).filter(models.User.role == "doctor").count()
    total_distributors = db.query(models.Distributor).filter(models.Distributor.role == "distributor").count()
    total_sub_admins = db.query(models.AdminStaff).filter(models.AdminStaff.role == "sub_admin").count()
    total_admins = db.query(models.AdminStaff).filter(models.AdminStaff.role == "admin").count()
    total_super_admins = db.query(models.SuperAdmin).filter(models.SuperAdmin.role == "super_admin").count()
    
    # Count orders - status is INTEGER in database
    total_orders = db.query(models.Order).count()
    pending_orders = db.query(models.Order).filter(models.Order.status == 0).count()
    confirmed_orders = db.query(models.Order).filter(models.Order.status == 1).count()
    delivered_orders = db.query(models.Order).filter(models.Order.status == 2).count()
    
    # Count products
    total_products = db.query(models.Product).count()
    distributor_products = db.query(models.Product).filter(models.Product.distributor_discount > 0).count()
    patient_products = total_products - distributor_products
    available_products = db.query(models.Product).filter(models.Product.is_available == True).count()
    
    # Revenue - handle None values
    all_orders = db.query(models.Order).all()
    total_revenue = sum([o.total_amount for o in all_orders if o.total_amount is not None])
    
    return {
        "users": {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_distributors": total_distributors,
            "total_sub_admins": total_sub_admins,
            "total_admins": total_admins,
            "total_super_admins": total_super_admins,
            "total_users": total_patients + total_doctors + total_distributors + total_sub_admins + total_admins + total_super_admins
        },
        "orders": {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "delivered_orders": delivered_orders
        },
        "products": {
            "total_products": total_products,
            "distributor_products": distributor_products,
            "patient_products": patient_products,
            "available_products": available_products
        },
        "revenue": {
            "total_revenue": total_revenue,
            "currency": "INR"
        }
    }

# UPDATE ORDER STATUS (ADMIN ONLY)
@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    0 = Pending
    1 = Confirmed
    2 = Delivered
    """

    check_admin_permission(request, required_role="sub_admin")

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise NotFoundException("Order not found")

    order.status = status

    db.commit()

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "new_status": (
            "PENDING" if status == 0 else
            "APPROVED" if status == 1 else
            "DELIVERED"
        )
    }

# GET ALL USERS (Admin can see all)

# GET ALL ORDERS (Admin view)
@router.get("/orders")
def get_all_orders(request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    orders = db.query(models.Order).order_by(models.Order.id.desc()).all()
    result = []
    for o in orders:
        product = db.query(models.Product).filter(models.Product.id == o.product_id).first()
        result.append({
            "id": o.id,
            "customer_name": o.customer_name,
            "product_name": product.product_name if product else "Unknown",
            "quantity": o.quantity,
            "final_amount": o.final_amount,
            "status": "PENDING" if o.status == 0 else "APPROVED" if o.status == 1 else "DELIVERED",
            "order_date": o.order_date
        })
    return result

# GET ALL PRODUCTS (Admin view)
@router.get("/products")
def get_all_products(request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    try:
        products = db.query(models.Product).filter(
            models.Product.product_status != "Deleted"
        ).order_by(models.Product.id.desc()).all()
        result = []
        for p in products:
            result.append({
                "id": p.id,
                "product_name": p.product_name,
                "product_type": p.product_type,
                "brand": p.brand,
                "model_name": p.model_name,
                "unit_price": p.unit_price,
                "unit_mrp": p.unit_mrp,
                "selling_price": p.selling_price,
                "discount": p.discount,
                "customer_discount": p.customer_discount,
                "distributor_discount": p.distributor_discount,
                "referral_discount": p.referral_discount,
                "tax_gst": p.tax_gst,
                "stock_pieces": p.stock_pieces,
                "product_status": p.product_status,
                "target_audience": p.target_audience,
                "currency": p.currency,
                "is_available": p.is_available,
                "description": p.description,
                "product_image": p.product_image,
                "product_images": p.product_images
            })
        return result
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Helper to safely get attribute from model
def safe_getattr(obj, name, default=None):
    return getattr(obj, name, default)

# GET ALL USERS (Admin can see all)
@router.get("/users")
def get_all_users(
    request: Request,
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)
):
    check_admin_permission(request, required_role="sub_admin")
    
    users = []
    if role:
        if role in ["patient", "doctor"]:
            users = db.query(models.User).filter(models.User.role == role).order_by(models.User.id.desc()).all()
        elif role == "distributor":
            users = db.query(models.Distributor).filter(models.Distributor.role == role).order_by(models.Distributor.id.desc()).all()
        elif role in ["admin", "sub_admin"]:
            users = db.query(models.AdminStaff).filter(models.AdminStaff.role == role).order_by(models.AdminStaff.id.desc()).all()
        elif role == "super_admin":
            users = db.query(models.SuperAdmin).filter(models.SuperAdmin.role == role).order_by(models.SuperAdmin.id.desc()).all()
    else:
        # Union all four tables and sort by creation time
        pats_docs = db.query(models.User).all()
        dists = db.query(models.Distributor).all()
        staff = db.query(models.AdminStaff).all()
        supers = db.query(models.SuperAdmin).all()
        users = pats_docs + dists + staff + supers
        users.sort(key=lambda u: u.created_at or datetime.min, reverse=True)
    
    return [{
        "id": u.id,
        "custom_id": u.custom_id,
        "name": u.name,
        "email": u.email,
        "role": u.role or (
            "distributor" if isinstance(u, models.Distributor) else
            "super_admin" if isinstance(u, models.SuperAdmin) else
            "admin" if isinstance(u, models.AdminStaff) else
            "patient"
        ),
        "phone": to_numeric_or_string(u.phone),
        "gender": u.gender,
        "age": to_numeric_or_string(u.age),
        "dob": u.dob,
        "homeAddress": u.home_address,
        "area": u.area,
        "district": u.district,
        "state": u.state,
        "pincode": to_numeric_or_string(u.pincode),
        "hospital": safe_getattr(u, "hospital"),
        "specialisation": safe_getattr(u, "specialisation"),
        "qualification": safe_getattr(u, "qualification"),
        "experience": safe_getattr(u, "experience"),
        "companyName": safe_getattr(u, "company_name"),
        "businessType": safe_getattr(u, "business_type"),
        "distributorType": safe_getattr(u, "distributor_type"),
        "licenseNumber": safe_getattr(u, "license_number"),
        "referralCode": safe_getattr(u, "referral_code"),
        "permissions": safe_getattr(u, "permissions"),
        "status": u.status or "Active",
        "verificationStatus": safe_getattr(u, "verification_status") or "Verified",
        "commission": safe_getattr(u, "commission") or 0.0,
        "discount": safe_getattr(u, "discount") or 0.0,
    } for u in users]

# VIEW SINGLE USER — GET /admin/users/{user_id}/view
@router.get("/users/{user_id}/view")
def view_user(
    user_id: int, 
    request: Request, 
    role: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    check_admin_permission(request, required_role="sub_admin")
    
    user = None
    if role:
        if role in ["patient", "doctor"]:
            user = db.query(models.User).filter(models.User.id == user_id).first()
        elif role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        elif role in ["admin", "sub_admin"]:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        elif role == "super_admin":
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        # Check all tables sequentially
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        if not user:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        if not user:
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        raise NotFoundException("User not found")

    total_orders = db.query(models.Order).filter(models.Order.user_id == user.id).count()

    return {
        "id": user.id,
        "customId": user.custom_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "phone": to_numeric_or_string(user.phone),
        "gender": user.gender,
        "age": to_numeric_or_string(user.age),
        "dob": user.dob,
        "homeAddress": user.home_address,
        "area": user.area,
        "district": user.district,
        "state": user.state,
        "pincode": to_numeric_or_string(user.pincode),
        "hospital": safe_getattr(user, "hospital"),
        "specialisation": safe_getattr(user, "specialisation"),
        "qualification": safe_getattr(user, "qualification"),
        "experience": safe_getattr(user, "experience"),
        "companyName": safe_getattr(user, "company_name"),
        "businessType": safe_getattr(user, "business_type"),
        "distributorType": safe_getattr(user, "distributor_type"),
        "licenseNumber": safe_getattr(user, "license_number"),
        "referralCode": safe_getattr(user, "referral_code"),
        "permissions": safe_getattr(user, "permissions"),
        "profileImage": user.profile_image,
        "status": user.status or "Active",
        "verificationStatus": safe_getattr(user, "verification_status") or "Verified",
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "lastLogin": user.last_login.isoformat() if user.last_login else None,
        "commission": safe_getattr(user, "commission") or 0.0,
        "discount": safe_getattr(user, "discount") or 0.0,
        "totalOrders": total_orders,
    }

# EDIT SINGLE USER — PUT /admin/users/{user_id}/edit
@router.put("/users/{user_id}/edit")
def edit_user(
    user_id: int, 
    update_data: UserUpdate, 
    request: Request, 
    role: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    check_admin_permission(request, required_role="admin")
    
    user = None
    if role:
        if role in ["patient", "doctor"]:
            user = db.query(models.User).filter(models.User.id == user_id).first()
        elif role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        elif role in ["admin", "sub_admin"]:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        elif role == "super_admin":
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        if not user:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        if not user:
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        raise NotFoundException("User not found")

    if user.role == "super_admin":
        check_admin_permission(request, required_role="super_admin")

    update_dict = update_data.dict(exclude_unset=True)

    # Email conflict check
    if "email" in update_dict and update_dict["email"] is not None:
        validated_email = validate_email(update_dict["email"])
        if is_email_taken_by_other(db, validated_email, user_id, user.role):
            raise ConflictException("Email already registered by another account")
        update_dict["email"] = validated_email

    if "permissions" in update_dict and update_dict["permissions"] is not None:
        check_admin_permission(request, required_role="super_admin")

    mapping = {
        "homeAddress": "home_address",
        "companyName": "company_name",
        "businessType": "business_type",
        "distributorType": "distributor_type",
        "licenseNumber": "license_number",
        "verificationStatus": "verification_status",
        "hospital": "hospital",
        "specialisation": "specialisation",
        "qualification": "qualification",
        "experience": "experience",
        "permissions": "permissions"
    }

    for key, value in update_dict.items():
        db_key = mapping.get(key, key)
        if hasattr(user, db_key):
            setattr(user, db_key, value)

    try:
        db.commit()
        db.refresh(user)
        return {"message": "User updated successfully", "user_id": user_id}
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to update user: {str(e)}")

# LEGACY — GET /admin/users/{user_id} (kept for backward compat)
@router.get("/users/{user_id}")
def get_user(user_id: int, request: Request, role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return view_user(user_id, request, role, db)

# LEGACY — PUT /admin/users/{user_id} (kept for backward compat)
@router.put("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdate, request: Request, role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return edit_user(user_id, update_data, request, role, db)

# DELETE USER (Only Super Admin)
@router.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request, role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Delete a user (Only Super Admin can do this)
    """
    check_admin_permission(request, required_role="super_admin")
    
    user = None
    if role:
        if role in ["patient", "doctor"]:
            user = db.query(models.User).filter(models.User.id == user_id).first()
        elif role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        elif role in ["admin", "sub_admin"]:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        elif role == "super_admin":
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        if not user:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        if not user:
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        raise NotFoundException("User not found")
    
    # Prevent deleting super admin
    if user.role == "super_admin":
        raise AuthorizationException("Cannot delete Super Admin!")
    
    try:
        # Delete dependent records to avoid IntegrityError using the user's specific ID
        db.query(models.SupportQuery).filter(models.SupportQuery.user_id == user.id).delete(synchronize_session=False)
        db.query(models.TherapyData).filter(models.TherapyData.patient_id == user.id).delete(synchronize_session=False)
        db.query(models.MachineSettings).filter((models.MachineSettings.patient_id == user.id) | (models.MachineSettings.doctor_id == user.id)).delete(synchronize_session=False)
        db.query(models.Notification).filter(models.Notification.user_id == user.id).delete(synchronize_session=False)
        db.query(models.PdfReportData).filter(models.PdfReportData.user_id == user.id).delete(synchronize_session=False)
        db.query(models.Order).filter(models.Order.user_id == user.id).delete(synchronize_session=False)
        
        # If user is a distributor, handle their products and orders for those products
        if user.role == "distributor":
            distributor_products = db.query(models.Product).filter(models.Product.distributor_id == user.id).all()
            for p in distributor_products:
                db.query(models.Order).filter(models.Order.product_id == p.id).delete(synchronize_session=False)
                db.delete(p)

        db.delete(user)
        db.commit()
        return {"message": f"User {user.name} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to delete user: {str(e)}")

# GET ALL ORDERS (Admin view)
@router.get("/orders")
def get_all_orders(request: Request, db: Session = Depends(get_db)):
    """
    Get all orders across all users
    """
    check_admin_permission(request, required_role="sub_admin")
    
    orders = db.query(models.Order).all()
    result = []
    
    for o in orders:
        product = db.query(models.Product).filter(models.Product.id == o.product_id).first()
        
        # Find order customer by querying User, then Distributor
        user = db.query(models.User).filter(models.User.id == o.user_id).first()
        if not user:
            user = db.query(models.Distributor).filter(models.Distributor.id == o.user_id).first()
        
        result.append({
            "order_id": o.id,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "user_role": user.role if user else "N/A",
            "product_name": product.product_name if product else "N/A",
            "product_type": product.product_type if product else "N/A",
            "quantity": o.quantity if o.quantity else 1,
            "total_amount": o.total_amount,
            "currency": o.currency,
            "status": (
                "PENDING" if o.status == 0 else
                "APPROVED" if o.status == 1 else
                "DELIVERED"
            ),
            "order_date": o.order_date,
        })
    
    return result
