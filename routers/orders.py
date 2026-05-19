from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import OrderCreate, OrderResponse, ReferralCreate
from utils import paginate

# Create router
router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ BUY MACHINE
@router.post("/buy-machine", response_model=OrderResponse)
def buy_machine(order: OrderCreate, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user

        if current_user["role"] not in ["patient", "doctor", "distributor"]:
            raise HTTPException(
                status_code=403,
                detail="Only patient, doctor or distributor can buy"
            )

        # CHECK PRODUCT
        product = db.query(models.Product).filter(
            models.Product.id == order.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # TOTAL PRICE
        total = product.unit_price * order.quantity

        discount_amount = 0
        final_amount = total    

        # ✅ APPLY REFERRAL DISCOUNT FROM REFERRAL_CODES OR FALLBACK USER REFERRAL
        discount_amount = 0
        final_amount = total    

        if order.referral_code:
            # 1. Check custom referral codes table first
            referral = db.query(models.ReferralCode).filter(
                models.ReferralCode.code == order.referral_code,
                models.ReferralCode.is_active == True,
                models.ReferralCode.role == current_user["role"]
            ).first()

            if referral:
                discount_percent = referral.discount_percent / 100.0
                discount_amount = total * discount_percent
                final_amount = total - discount_amount
                # Increment used count
                referral.used_count = (referral.used_count or 0) + 1
            else:
                # 2. Fallback to check if it's another user's referral code
                referral_user = db.query(models.User).filter(
                    models.User.referral_code == order.referral_code
                ).first()

                if referral_user:
                    discount_amount = total * 0.10  # Default 10% for user referrals
                    final_amount = total - discount_amount
        # CREATE ORDER
        new_order = models.Order(
            user_id=current_user["user_id"],
            product_id=order.product_id,
            quantity=order.quantity,
            referral_code=order.referral_code,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            total_amount=total,
            discount_amount=discount_amount,
            final_amount=final_amount,
            currency="INR",
            building=order.building,
            locality=order.locality,
            district=order.district,
            state=order.state,
            pincode=order.pincode,
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        print(f"Order Created: {new_order.id}")

        return {
            "id": new_order.id,
            "product_id": new_order.product_id,
            "quantity": new_order.quantity,
            "total_amount": new_order.total_amount,
            "discount_amount": new_order.discount_amount,
            "final_amount": new_order.final_amount,
            "status": "PENDING", # Explicitly return string as per schema
            "order_date": new_order.order_date
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        print("BUY MACHINE ERROR:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ✅ MY ORDERS (With Pagination)
@router.get("/my-orders")
def my_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(40, ge=1, le=100, description="Items per page"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Get user's orders with pagination
    """
    current_user = request.state.user
    query = db.query(models.Order).filter(models.Order.user_id == current_user["user_id"])
    
    # Get paginated orders
    paginated = paginate(query, page=page, limit=limit)
    
    # Transform data
    result = []
    for o in paginated["data"]:
        product = db.query(models.Product).filter(models.Product.id == o.product_id).first()
        result.append({
            "order_id": o.id,
            "product_name": product.product_name if product else "N/A",
            "product_type": product.product_type if product else "N/A",
            "product_image": product.product_image if product else None,
            "quantity": o.quantity if o.quantity else 1,
            "unit_price": product.unit_price if product else None,
            "unit_mrp": product.unit_mrp if product else None,
            "discount": product.discount if product else None,
            "total_amount": o.total_amount,
            "discount_amount": o.discount_amount,
            "final_amount": o.final_amount,
            "currency": o.currency,
            "status": (
                "PENDING" if o.status == 0 else
                "APPROVED" if o.status == 1 else
                "DELIVERED"
            ),
            "order_date": o.order_date,
            "referral_code": o.referral_code,
            "delivery_address": {
                "name": o.customer_name,
                "phone": o.customer_phone,
                "building": o.building,
                "locality": o.locality,
                "district": o.district,
                "state": o.state,
                "pincode": o.pincode,
            }
        })
    
    # Return with pagination info
    return {
        "total": paginated["total"],
        "page": paginated["page"],
        "limit": paginated["limit"],
        "total_pages": paginated["total_pages"],
        "has_next": paginated["has_next"],
        "has_prev": paginated["has_prev"],
        "data": result
    }

# ✅ CREATE REFERRAL
@router.post("/create-referral")
def create_referral(referral: ReferralCreate, db: Session = Depends(get_db)):
    try:
        if db.query(models.ReferralCode).filter(models.ReferralCode.code == referral.code).first():
            raise HTTPException(status_code=400, detail="Code already exists")
        db.add(models.ReferralCode(
            code=referral.code,
            role=referral.role,
            discount_percent=referral.discount_percent))
        db.commit()
        return {"message": "Referral code created!", "code": referral.code, "discount": referral.discount_percent}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ VERIFY REFERRAL
@router.get("/verify-referral/{code}")
def verify_referral(code: str, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    
    # 1. Check custom referral codes table first
    referral = db.query(models.ReferralCode).filter(
        models.ReferralCode.code == code,
        models.ReferralCode.is_active == True,
        models.ReferralCode.role == current_user["role"]
    ).first()
    
    if referral:
        return {
            "message": "Referral code valid ✅",
            "code": referral.code,
            "discount_percent": referral.discount_percent,
            "valid_for": referral.role,
            "used_count": referral.used_count,
        }
        
    # 2. Check fallback: User referral code (from users table)
    referral_user = db.query(models.User).filter(
        models.User.referral_code == code
    ).first()
    
    if referral_user:
        return {
            "message": "User referral valid ✅",
            "code": code,
            "discount_percent": 10.0,  # Default 10% initial/default discount
            "valid_for": current_user["role"],
            "used_count": 0,
        }
        
    raise HTTPException(status_code=404, detail="Invalid or expired referral code")