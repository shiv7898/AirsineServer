import json
import random
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from core.database import SessionLocal
import models
from schemas import UserCreate, UserResponse, UserUpdate
from core.security import hash_password, create_token
from helpers.validators import (
    validate_email, validate_password, validate_phone,
    validate_pincode, validate_age, validate_role, to_numeric_or_string
)
from core.exceptions import (
    ConflictException, AuthorizationException, NotFoundException, DatabaseException
)
from services.user_service import UserService

router = APIRouter(tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_admin_permission(request: Request, required_role: str = "sub_admin"):
    current_user = request.state.user
    
    if required_role == "super_admin":
        if current_user["role"] != "super_admin":
            raise AuthorizationException("Only Super Admin can perform this action")
    else:
        if current_user["role"] not in ["admin", "sub_admin", "super_admin"]:
            raise AuthorizationException("Admin access required")
    
    return current_user

def parse_permissions(permissions_val) -> dict:
    if not permissions_val:
        return {}
    if isinstance(permissions_val, dict):
        return permissions_val
    if isinstance(permissions_val, str):
        try:
            return json.loads(permissions_val)
        except Exception:
            return {}
    return {}

def is_email_taken(db: Session, email: str) -> bool:
    return UserService.is_email_taken(db, email)

def is_email_taken_by_other(db: Session, email: str, exclude_user_id: int, exclude_role: str) -> bool:
    email_lower = email.lower().strip()
    
    patient = db.query(models.Patient).filter(models.Patient.email == email_lower).first()
    if patient and not (exclude_role == "patient" and patient.id == exclude_user_id):
        return True
        
    doctor = db.query(models.Doctor).filter(models.Doctor.email == email_lower).first()
    if doctor and not (exclude_role == "doctor" and doctor.id == exclude_user_id):
        return True
        
    dist = db.query(models.Distributor).filter(models.Distributor.email == email_lower).first()
    if dist and not (exclude_role == "distributor" and dist.id == exclude_user_id):
        return True
        
    staff = db.query(models.AdminStaff).filter(models.AdminStaff.email == email_lower).first()
    if staff and not (exclude_role in ["admin", "sub_admin"] and staff.id == exclude_user_id):
        return True
        
    sp = db.query(models.SuperAdmin).filter(models.SuperAdmin.email == email_lower).first()
    if sp and not (exclude_role == "super_admin" and sp.id == exclude_user_id):
        return True
        
    return False

@router.post("/create-super-admin", response_model=UserResponse)
def create_super_admin(
    user: UserCreate,
    secret_key: str = Query(..., description="Secret key to create super admin"),
    db: Session = Depends(get_db)
):
    SUPER_ADMIN_SECRET = "AIRSINE_HOSPITAL_2026_SECRET"
    
    if secret_key != SUPER_ADMIN_SECRET:
        raise AuthorizationException("Invalid secret key! Unauthorized access.")
    
    existing_super_admin = db.query(models.SuperAdmin).filter(
        models.SuperAdmin.role == "super_admin"
    ).first()
    
    if existing_super_admin:
        raise ConflictException("Super Admin already exists! Contact system administrator.")
    
    validated_email = validate_email(user.email)
    if is_email_taken(db, validated_email):
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
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

@router.post("/create-staff", response_model=UserResponse)
def create_staff(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="super_admin")
    
    validated_role = validate_role(user.role)
    if validated_role not in ["admin", "sub_admin"]:
        raise HTTPException(status_code=400, detail="Invalid staff role. Must be 'admin' or 'sub_admin'")
        
    validated_email = validate_email(user.email)
    if is_email_taken(db, validated_email):
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
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
        new_staff.custom_id = generate_custom_id_for_db(db, validated_role)
        db.commit()
        db.refresh(new_staff)
        return new_staff
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create staff member: {str(e)}")

def generate_custom_id_for_db(db: Session, role: str) -> str:
    return UserService.generate_custom_id(db, role)

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    
    validated_role = validate_role(user.role)
    if validated_role not in ["patient", "doctor", "distributor"]:
        raise HTTPException(status_code=400, detail="Role must be 'patient', 'doctor', or 'distributor'")
        
    validated_email = validate_email(user.email)
    if is_email_taken(db, validated_email):
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
    custom_id = generate_custom_id_for_db(db, validated_role)
    
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
            referral_code=UserService.generate_unique_referral_code(db),
            status="Active",
            verification_status="Verified"
        )
    elif validated_role == "doctor":
        new_user = models.Doctor(
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
            referral_code=UserService.generate_unique_referral_code(db),
            status="Active",
            verification_status="Verified"
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
            status="Active",
            verification_status="Verified"
        )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create user: {str(e)}")

@router.get("/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    
    total_patients = db.query(models.Patient).count()
    total_doctors = db.query(models.Doctor).count()
    total_distributors = db.query(models.Distributor).filter(models.Distributor.role == "distributor").count()
    total_sub_admins = db.query(models.AdminStaff).filter(models.AdminStaff.role == "sub_admin").count()
    total_admins = db.query(models.AdminStaff).filter(models.AdminStaff.role == "admin").count()
    total_super_admins = db.query(models.SuperAdmin).filter(models.SuperAdmin.role == "super_admin").count()
    
    total_orders = db.query(models.Order).count()
    pending_orders = db.query(models.Order).filter(models.Order.status == 0).count()
    confirmed_orders = db.query(models.Order).filter(models.Order.status == 1).count()
    delivered_orders = db.query(models.Order).filter(models.Order.status == 2).count()
    
    total_products = db.query(models.Product).count()
    distributor_products = db.query(models.Product).filter(models.Product.distributor_discount > 0).count()
    patient_products = total_products - distributor_products
    available_products = db.query(models.Product).filter(models.Product.is_available == True).count()
    
    all_orders = db.query(models.Order).all()
    total_revenue = sum([o.total_amount for o in all_orders if o.total_amount is not None])
    
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    past_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    past_7_days_str = [d.strftime("%Y-%m-%d") for d in past_7_days]
    
    weekly_distributor = [0] * 7
    weekly_doctor = [0] * 7
    weekly_patient = [0] * 7
    
    start_date = datetime.utcnow() - timedelta(days=7)
    recent_orders = db.query(models.Order).filter(models.Order.order_date >= start_date).all()
    
    for o in recent_orders:
        if not o.order_date: continue
        o_date_str = o.order_date.date().strftime("%Y-%m-%d")
        if o_date_str in past_7_days_str:
            idx = past_7_days_str.index(o_date_str)
            if o.user_role == "distributor":
                weekly_distributor[idx] += 1
            elif o.user_role == "doctor":
                weekly_doctor[idx] += 1
            else:
                weekly_patient[idx] += 1
    
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
        },
        "weekly_stats": {
            "labels": [d.strftime("%a") for d in past_7_days],
            "distributor": weekly_distributor,
            "doctor": weekly_doctor,
            "patient": weekly_patient
        }
    }

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: int,
    request: Request,
    db: Session = Depends(get_db)
):
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

@router.get("/orders")
def get_all_orders(request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    orders = db.query(models.Order).order_by(models.Order.id.desc()).all()
    result = []
    for o in orders:
        product = db.query(models.Product).filter(models.Product.id == o.product_id).first()
        
        user_data = None
        if o.user_role == "patient":
            user = db.query(models.Patient).filter(models.Patient.id == o.user_id).first()
        elif o.user_role == "doctor":
            user = db.query(models.Doctor).filter(models.Doctor.id == o.user_id).first()
        elif o.user_role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == o.user_id).first()
        else:
            user = None
            
        if user:
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "custom_id": user.custom_id,
                "age": user.age,
                "gender": user.gender
            }
            
        product_data = None
        if product:
            product_data = {
                "id": product.id,
                "product_name": product.product_name,
                "product_type": product.product_type,
                "brand": product.brand,
                "model_name": product.model_name,
                "unit_price": product.unit_price,
                "selling_price": product.selling_price
            }

        result.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "quantity": o.quantity,
            "total_amount": o.total_amount,
            "discount_amount": o.discount_amount,
            "mrp_amount": o.mrp_amount,
            "product_discount_amount": o.product_discount_amount,
            "referral_discount_amount": o.referral_discount_amount,
            "gst_amount": o.gst_amount,
            "final_amount": o.final_amount,
            "status": "PENDING" if o.status == 0 else "APPROVED" if o.status == 1 else "DELIVERED",
            "order_date": o.order_date,
            "building": o.building,
            "locality": o.locality,
            "district": o.district,
            "state": o.state,
            "pincode": o.pincode,
            "referral_code": o.referral_code,
            "product_name": product.product_name if product else "Unknown",
            "product": product_data,
            "user": user_data
        })
    return result

@router.get("/products")
def get_all_products(request: Request, db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    try:
        from sqlalchemy import or_
        products = db.query(models.Product).filter(
            or_(
                models.Product.product_status != "Deleted",
                models.Product.product_status.is_(None)
            )
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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def safe_getattr(obj, name, default=None):
    return getattr(obj, name, default)

@router.get("/users")
def get_all_users(
    request: Request,
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)
):
    check_admin_permission(request, required_role="sub_admin")
    
    users = []
    if role:
        if role == "patient":
            users = db.query(models.Patient).filter(models.Patient.role == role).order_by(models.Patient.id.desc()).all()
        elif role == "doctor":
            users = db.query(models.Doctor).filter(models.Doctor.role == role).order_by(models.Doctor.id.desc()).all()
        elif role == "distributor":
            users = db.query(models.Distributor).filter(models.Distributor.role == role).order_by(models.Distributor.id.desc()).all()
        elif role in ["admin", "sub_admin"]:
            users = db.query(models.AdminStaff).filter(models.AdminStaff.role == role).order_by(models.AdminStaff.id.desc()).all()
        elif role == "super_admin":
            users = db.query(models.SuperAdmin).filter(models.SuperAdmin.role == role).order_by(models.SuperAdmin.id.desc()).all()
    else:
        pats = db.query(models.Patient).all()
        docs = db.query(models.Doctor).all()
        dists = db.query(models.Distributor).all()
        staff = db.query(models.AdminStaff).all()
        supers = db.query(models.SuperAdmin).all()
        users = pats + docs + dists + staff + supers
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
        if role == "patient":
            user = db.query(models.Patient).filter(models.Patient.id == user_id).first()
        elif role == "doctor":
            user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
        elif role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        elif role in ["admin", "sub_admin"]:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        elif role == "super_admin":
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        user = db.query(models.Patient).filter(models.Patient.id == user_id).first()
        if not user:
            user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
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

@router.put("/users/{user_id}/edit")
def edit_user(
    user_id: int, 
    update_data: UserUpdate, 
    request: Request, 
    role: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    check_admin_permission(request, required_role="sub_admin")
    current_user = request.state.user
    
    user = None
    if role:
        if role == "patient":
            user = db.query(models.Patient).filter(models.Patient.id == user_id).first()
        elif role == "doctor":
            user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
        elif role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        elif role in ["admin", "sub_admin"]:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        elif role == "super_admin":
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        user = db.query(models.Patient).filter(models.Patient.id == user_id).first()
        if not user:
            user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
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

    if current_user["role"] in ["admin", "sub_admin"]:
        staff_db = db.query(models.AdminStaff).filter(models.AdminStaff.id == current_user["user_id"]).first()
        if not staff_db:
             raise AuthorizationException("Admin account not found")
        
        target_module = "users"
        if user.role in ["admin", "sub_admin"]:
            target_module = "staff"
        elif user.role == "distributor":
            target_module = "distributors"
            
        perms = parse_permissions(staff_db.permissions)
        if target_module not in perms or "edit" not in perms.get(target_module, []):
            raise AuthorizationException(f"You don't have permission to edit {target_module}")

    update_dict = update_data.dict(exclude_unset=True)

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

@router.get("/users/{user_id}")
def get_user(user_id: int, request: Request, role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return view_user(user_id, request, role, db)

@router.put("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdate, request: Request, role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return edit_user(user_id, update_data, request, role, db)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request, role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    check_admin_permission(request, required_role="sub_admin")
    current_user = request.state.user
    
    user = None
    if role:
        if role == "patient":
            user = db.query(models.Patient).filter(models.Patient.id == user_id).first()
        elif role == "doctor":
            user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
        elif role == "distributor":
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        elif role in ["admin", "sub_admin"]:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        elif role == "super_admin":
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        user = db.query(models.Patient).filter(models.Patient.id == user_id).first()
        if not user:
            user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
        if not user:
            user = db.query(models.Distributor).filter(models.Distributor.id == user_id).first()
        if not user:
            user = db.query(models.AdminStaff).filter(models.AdminStaff.id == user_id).first()
        if not user:
            user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
            
    if not user:
        raise NotFoundException("User not found")
    
    if user.role == "super_admin":
        raise AuthorizationException("Cannot delete Super Admin!")

    if current_user["role"] in ["admin", "sub_admin"]:
        staff_db = db.query(models.AdminStaff).filter(models.AdminStaff.id == current_user["user_id"]).first()
        if not staff_db:
             raise AuthorizationException("Admin account not found")
        
        target_module = "users"
        if user.role in ["admin", "sub_admin"]:
            target_module = "staff"
        elif user.role == "distributor":
            target_module = "distributors"
            
        perms = parse_permissions(staff_db.permissions)
        if target_module not in perms or "delete" not in perms.get(target_module, []):
            raise AuthorizationException(f"You don't have permission to delete {target_module}")
    
    try:
        db.query(models.SupportQuery).filter(models.SupportQuery.user_id == user.id).delete(synchronize_session=False)
        db.query(models.TherapyData).filter(models.TherapyData.patient_id == user.id).delete(synchronize_session=False)
        db.query(models.MachineSettings).filter((models.MachineSettings.patient_id == user.id) | (models.MachineSettings.doctor_id == user.id)).delete(synchronize_session=False)
        db.query(models.Notification).filter(models.Notification.user_id == user.id).delete(synchronize_session=False)
        db.query(models.PdfReportData).filter(models.PdfReportData.user_id == user.id).delete(synchronize_session=False)
        db.query(models.Order).filter(models.Order.user_id == user.id).delete(synchronize_session=False)
        
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
