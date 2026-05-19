from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import UserCreate, UserResponse
from auth import hash_password, create_token
from validators import validate_email, validate_password, validate_phone, validate_pincode, validate_age, validate_role
from exception import ConflictException, AuthorizationException, NotFoundException, DatabaseException
from typing import Optional

# Create router
router = APIRouter(
    prefix="/admin",
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
    required_role: 'sub_admin' or 'super_admin'
    """
    current_user = request.state.user
    
    if required_role == "super_admin":
        if current_user["role"] != "super_admin":
            raise AuthorizationException("Only Super Admin can perform this action")
    else:  # sub_admin or super_admin allowed
        if current_user["role"] not in ["sub_admin", "super_admin"]:
            raise AuthorizationException("Admin access required")
    
    return current_user

# CREATE SUPER ADMIN (Protected with secret key)
@router.post("/create-super-admin", response_model=UserResponse)
def create_super_admin(
    user: UserCreate,
    secret_key: str = Query(..., description="Secret key to create super admin"),  # ADDED
    db: Session = Depends(get_db)
):
    """
    Create the first super admin (Protected with secret key)
    Only works once and requires secret key
    """
    # CHECK SECRET KEY FIRST
    SUPER_ADMIN_SECRET = "AIRSINE_HOSPITAL_2026_SECRET"  # Change this to your own secret!
    
    if secret_key != SUPER_ADMIN_SECRET:
        raise AuthorizationException("Invalid secret key! Unauthorized access.")
    
    # Check if super admin already exists
    existing_super_admin = db.query(models.User).filter(
        models.User.role == "super_admin"
    ).first()
    
    if existing_super_admin:
        raise ConflictException("Super Admin already exists! Contact system administrator.")
    
    # Validate
    validated_email = validate_email(user.email)
    if db.query(models.User).filter(models.User.email == validated_email).first():
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
    # Create super admin
    new_admin = models.User(
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

# CREATE SUB ADMIN (Only Super Admin can do this)
@router.post("/create-sub-admin", response_model=UserResponse)
def create_sub_admin(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a sub-admin (Only Super Admin can do this)
    """
    # Check permission
    check_admin_permission(request, required_role="super_admin")
    
    # Validate
    validated_email = validate_email(user.email)
    if db.query(models.User).filter(models.User.email == validated_email).first():
        raise ConflictException("Email already registered")
    
    validated_password = validate_password(user.password)
    validated_phone = validate_phone(user.phone)
    validated_age = validate_age(user.age)
    validated_pincode = validate_pincode(user.pincode)
    
    # Create sub admin
    new_sub_admin = models.User(
        name=user.name.strip(),
        email=validated_email,
        password=hash_password(validated_password),
        role="sub_admin",  # Force sub_admin role
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
        db.add(new_sub_admin)
        db.commit()
        db.refresh(new_sub_admin)
        return new_sub_admin
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Failed to create sub admin: {str(e)}")

# ADMIN DASHBOARD
@router.get("/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Get admin dashboard statistics
    """
    check_admin_permission(request, required_role="sub_admin")
    
    # Count users by role
    total_patients = db.query(models.User).filter(models.User.role == "patient").count()
    total_doctors = db.query(models.User).filter(models.User.role == "doctor").count()
    total_distributors = db.query(models.User).filter(models.User.role == "distributor").count()
    total_sub_admins = db.query(models.User).filter(models.User.role == "sub_admin").count()
    
    # Count orders - status is INTEGER in database
    total_orders = db.query(models.Order).count()
    pending_orders = db.query(models.Order).filter(models.Order.status == 0).count()
    confirmed_orders = db.query(models.Order).filter(models.Order.status == 1).count()
    delivered_orders = db.query(models.Order).filter(models.Order.status == 2).count()
    
    # Count products
    total_products = db.query(models.Product).count()
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
            "total_users": total_patients + total_doctors + total_distributors
        },
        "orders": {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "delivered_orders": delivered_orders
        },
        "products": {
            "total_products": total_products,
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
@router.get("/users")
def get_all_users(
    request: Request,
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)
):
    """
    Get all users (with optional role filter)
    """
    check_admin_permission(request, required_role="sub_admin")
    
    query = db.query(models.User)
    
    if role:
        query = query.filter(models.User.role == role)
    
    users = query.all()
    
    return [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "phone": u.phone,
        "gender": u.gender,
        "age": u.age,
    } for u in users]

# DELETE USER (Only Super Admin)
@router.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Delete a user (Only Super Admin can do this)
    """
    check_admin_permission(request, required_role="super_admin")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    
    # Prevent deleting super admin
    if user.role == "super_admin":
        raise AuthorizationException("Cannot delete Super Admin!")
    
    try:
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
        user = db.query(models.User).filter(models.User.id == o.user_id).first()
        
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