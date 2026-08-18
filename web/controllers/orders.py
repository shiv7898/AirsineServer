from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from core.database import SessionLocal
import models
from schemas import OrderCreate, OrderResponse, ReferralCreate
from helpers.utils import paginate
from services.order_service import OrderService

router = APIRouter(tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/customer/buy-machine", response_model=OrderResponse)
def buy_machine_customer(order: OrderCreate, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] not in ["patient", "doctor"]:
        raise HTTPException(status_code=403, detail="Only patient or doctor can buy through this API")

    try:
        new_order = OrderService.create_order(
            db=db,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            product_id=order.product_id,
            quantity=order.quantity,
            customer_name=order.customer_name,
            customer_phone=str(order.customer_phone),
            building=order.building,
            locality=order.locality,
            district=order.district,
            state=order.state,
            pincode=str(order.pincode),
            referral_code=order.referral_code,
        )
        return {
            "id": new_order.id,
            "product_id": new_order.product_id,
            "quantity": new_order.quantity,
            "total_amount": new_order.total_amount,
            "discount_amount": new_order.discount_amount,
            "final_amount": new_order.final_amount,
            "status": "PENDING",
            "order_date": new_order.order_date,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distributor/buy-machine", response_model=OrderResponse)
def buy_machine_distributor(order: OrderCreate, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Only distributor can buy through this API")

    try:
        new_order = OrderService.create_order(
            db=db,
            user_id=current_user["user_id"],
            user_role="distributor",
            product_id=order.product_id,
            quantity=order.quantity,
            customer_name=order.customer_name,
            customer_phone=str(order.customer_phone),
            building=order.building,
            locality=order.locality,
            district=order.district,
            state=order.state,
            pincode=str(order.pincode),
            referral_code=None,
        )
        return {
            "id": new_order.id,
            "product_id": new_order.product_id,
            "quantity": new_order.quantity,
            "total_amount": new_order.total_amount,
            "discount_amount": new_order.discount_amount,
            "final_amount": new_order.final_amount,
            "status": "PENDING",
            "order_date": new_order.order_date,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-orders")
def my_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(40, ge=1, le=100, description="Items per page"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    query = db.query(models.Order).filter(models.Order.user_id == current_user["user_id"]).order_by(models.Order.order_date.desc())
    
    paginated = paginate(query, page=page, limit=limit)
    
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
    
    return {
        "total": paginated["total"],
        "page": paginated["page"],
        "limit": paginated["limit"],
        "total_pages": paginated["total_pages"],
        "has_next": paginated["has_next"],
        "has_prev": paginated["has_prev"],
        "data": result
    }

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

@router.get("/verify-referral/{code}")
def verify_referral(code: str, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    
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
        
    referral_user = db.query(models.Patient).filter(
        models.Patient.referral_code == code
    ).first() or db.query(models.Doctor).filter(
        models.Doctor.referral_code == code
    ).first()
    
    if referral_user:
        return {
            "message": "User referral valid ✅",
            "code": code,
            "discount_percent": 10.0,
            "valid_for": current_user["role"],
            "used_count": 0,
        }
        
    raise HTTPException(status_code=404, detail="Invalid or expired referral code")
