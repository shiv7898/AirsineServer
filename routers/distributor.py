from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import os, shutil
from datetime import datetime
from utils import paginate
from schemas import OrderCreate, OrderResponse

router = APIRouter(
    prefix="/distributor",
    tags=["Distributor"]
)

# Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DISTRIBUTOR SECTION
@router.get("/")
def distributor_section(request: Request, db: Session = Depends(get_db)):
    user = request.state.user

    if user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    db_user = db.query(models.User).filter(
        models.User.id == user["user_id"]
    ).first()

    return {
        "message": "Welcome Distributor!",
        "data": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone,
            "company_name": db_user.company_name,
            "business_type": db_user.business_type,
            "distributor_type": db_user.distributor_type,
            "license_number": db_user.license_number,
            "referral_code": db_user.referral_code,

        }
    }

# DISTRIBUTOR ALL ORDERS (Filtered by products they own)
@router.get("/orders")
def distributor_orders(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    # Join with Product to filter by distributor_id
    orders = db.query(models.Order).join(models.Product).filter(
        models.Product.distributor_id == current_user["user_id"]
    ).all()

    result = []

    for o in orders:
        product = db.query(models.Product).filter(
            models.Product.id == o.product_id
        ).first()

        result.append({
            "order_id": o.id,
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
            "customer": {
                "name": o.customer_name,
                "phone": o.customer_phone,
                "building": o.building,
                "locality": o.locality,
                "district": o.district,
                "state": o.state,
                "pincode": o.pincode,
            }
        })

    return result

# DISTRIBUTOR DASHBOARD (Filtered)
@router.get("/dashboard")
def distributor_dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    # Filter orders by products owned by this distributor
    orders_query = db.query(models.Order).join(models.Product).filter(
        models.Product.distributor_id == current_user["user_id"]
    )
    
    total_orders = orders_query.count()

    confirmed = orders_query.filter(
        models.Order.status == 1
    ).count()

    pending = orders_query.filter(
        models.Order.status == 0
    ).count()

    delivered = orders_query.filter(
        models.Order.status == 2
    ).count()

    revenue = sum([
        o.total_amount for o in orders_query.all()
        if o.status != 0 and o.total_amount is not None
    ])

    return {
        "total_orders": total_orders,
        "confirmed_orders": confirmed,
        "pending_orders": pending,
        "delivered_orders": delivered,
        "total_revenue": revenue,
        "currency": "INR"
    }


# DISTRIBUTOR TRANSACTIONS (Filtered)
@router.get("/transactions")
def distributor_transactions(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    orders = db.query(models.Order).join(models.Product).filter(
        models.Product.distributor_id == current_user["user_id"]
    ).order_by(
        models.Order.order_date.desc()
    ).limit(10).all()

    result = []

    for o in orders:
        product = db.query(models.Product).filter(
            models.Product.id == o.product_id
        ).first()

        result.append({
            "order_id": o.id,
            "product_name": product.product_name if product else "N/A",
            "product_type": product.product_type if product else "N/A",
            "quantity": o.quantity,
            "total_amount": o.total_amount,
            "currency": o.currency,
            "status": (
                "PENDING" if o.status == 0 else
                "APPROVED" if o.status == 1 else
                "DELIVERED"
            ),
            "order_date": o.order_date,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
        })

    return result

# ✅ ADD PRODUCT (Distributor Specific)
@router.post("/add-product")
def distributor_add_product(
    request: Request,
    product_name: str = Form(...),
    product_type: str = Form(...),
    unit_price: float = Form(...),
    unit_mrp: float = Form(...),
    discount: float = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Only distributors can add products here")

    try:
        image_filename = None
        os.makedirs("uploads/products", exist_ok=True)

        if image:
            extension = image.filename.split(".")[-1]
            image_filename = f"dist_{current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{extension}"
            image_path = f"uploads/products/{image_filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        new_product = models.Product(
            product_name=product_name,
            product_type=product_type,
            unit_price=unit_price,
            unit_mrp=unit_mrp,
            discount=discount,
            description=description,
            product_image=image_filename,
            distributor_id=current_user["user_id"] # Link to distributor
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return {"message": "Product added successfully", "product_id": new_product.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ✅ MY PRODUCTS (List products added by this distributor)
@router.get("/my-products")
def get_my_products(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    query = db.query(models.Product).filter(
        models.Product.distributor_id == current_user["user_id"]
    )

    products_data = paginate(query, page=page, limit=limit)

    for product in products_data["data"]:
        if product.product_image:
            product.image_url = f"{request.base_url}uploads/products/{product.product_image}"
        else:
            product.image_url = None

    return products_data

# ✅ BUY MACHINE (Placed by Distributor)
@router.post("/buy-machine")
def distributor_buy_machine(
    order: OrderCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # CHECK PRODUCT
        product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # TOTAL PRICE
        total = product.unit_price * order.quantity
        discount_amount = 0
        final_amount = total

        # APPLY REFERRAL DISCOUNT IF ANY
        if order.referral_code:
            referral_user = db.query(models.User).filter(models.User.referral_code == order.referral_code).first()
            if referral_user:
                discount_amount = total * 0.10
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
            status=0 # PENDING
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return {
            "message": "Order placed successfully",
            "order_id": new_order.id,
            "status": "PENDING"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ✅ MY ORDERS (Orders placed BY this distributor)
@router.get("/my-orders")
def get_distributor_personal_orders(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    query = db.query(models.Order).filter(
        models.Order.user_id == current_user["user_id"]
    ).order_by(models.Order.order_date.desc())

    orders_data = paginate(query, page=page, limit=limit)

    result_data = []
    for o in orders_data["data"]:
        product = db.query(models.Product).filter(models.Product.id == o.product_id).first()
        result_data.append({
            "order_id": o.id,
            "product_name": product.product_name if product else "N/A",
            "quantity": o.quantity,
            "final_amount": o.final_amount,
            "status": (
                "PENDING" if o.status == 0 else
                "APPROVED" if o.status == 1 else
                "DELIVERED"
            ),
            "order_date": o.order_date
        })

    return {
        "total": orders_data["total"],
        "page": orders_data["page"],
        "limit": orders_data["limit"],
        "data": result_data
    }

# ✅ DISTRIBUTOR SUMMARY (Modern UI)
@router.get("/summary")
def get_distributor_summary(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    # Base query for orders related to this distributor's products
    orders_query = db.query(models.Order).join(models.Product).filter(
        models.Product.distributor_id == current_user["user_id"]
    )
    
    total_received = orders_query.count()
    
    # 1. Total Sales (Only Approved or Delivered, using total_amount before any auto-discount)
    revenue = sum([
        o.total_amount for o in orders_query.all()
        if o.status != 0 and o.total_amount is not None
    ])

    # 2. Net Profit (Estimated at 20%)
    profit = revenue * 0.20

    # 3. Pending Orders (Status 0)
    pending_orders_count = orders_query.filter(models.Order.status == 0).count()

    # 4. Pending Queries (Count for this distributor)
    pending_queries = db.query(models.Notification).filter(
        models.Notification.user_id == current_user["user_id"],
        models.Notification.title.like("Support Query%"),
        models.Notification.is_read == False
    ).count()

    # Formatting Helper
    def format_currency(val):
        if val >= 100000:
            return f"₹{val/100000:.1f}L"
        if val >= 1000:
            return f"₹{val/1000:.0f}K"
        return f"₹{val:.0f}"

    return {
        "sales": {
            "title": "Total Sales",
            "value": format_currency(revenue),
            "subtitle": "Overall",
            "icon": "currency-inr",
            "color": "#0ea5e9"
        },
        "profit": {
            "title": "Net Profit",
            "value": format_currency(profit),
            "subtitle": "Estimated (20%)",
            "icon": "trending-up",
            "color": "#10B981"
        },
        "orders": {
            "title": "Pending Orders",
            "value": f"{pending_orders_count:02d}",
            "unit": "units",
            "subtitle": f"Total: {total_received}",
            "icon": "package-variant",
            "color": "#8B5CF6"
        },
        "queries": {
            "title": "Support Queries",
            "value": f"{pending_queries:02d}",
            "unit": "pending",
            "subtitle": "Support",
            "icon": "message-alert-outline",
            "color": "#F59E0B"
        }
    }

# ✅ DISTRIBUTOR SUPPORT QUERY (With Image)
@router.post("/support-query")
def distributor_support_query(
    request: Request,
    category: str = Form(...),
    message: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Fetch user details
        user_db = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        image_filename = None
        os.makedirs("uploads/support", exist_ok=True)

        if image:
            extension = image.filename.split(".")[-1]
            image_filename = f"supp_{current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{extension}"
            image_path = f"uploads/support/{image_filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        new_query = models.Notification(
            user_id=current_user["user_id"],
            title=f"Support Query - {category}",
            message=message,
            image=image_filename,
            user_name=user_db.name,
            user_email=user_db.email,
            user_role=user_db.role,
            is_read=False
        )

        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        
        return {"message": "Query submitted successfully", "query_id": new_query.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
