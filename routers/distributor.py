from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
import models
import os, shutil
from datetime import datetime, timedelta, date
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

# DISTRIBUTOR ALL ORDERS (Filtered to show distributor's own orders)
@router.get("/orders")
def distributor_orders(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    # Filter to show the distributor's own orders
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user["user_id"]
    ).order_by(models.Order.order_date.desc()).all()

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
            "discount_amount": o.discount_amount or 0,
            "final_amount": o.final_amount if o.final_amount is not None else o.total_amount,
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


# DISTRIBUTOR TRANSACTIONS (Filtered to show distributor's own orders)
@router.get("/transactions")
def distributor_transactions(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user["user_id"]
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
            "discount_amount": o.discount_amount or 0,
            "final_amount": o.final_amount if o.final_amount is not None else o.total_amount,
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
    limit: int = Query(20, ge=1, le=100),
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

    # Base query for orders placed by the distributor themselves
    orders_query = db.query(models.Order).filter(
        models.Order.user_id == current_user["user_id"]
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

    # Calculate total machines purchased by the distributor themselves
    machines_purchased = orders_query.count()

    # Formatting Helper
    def format_currency(val):
        if val >= 100000:
            return f"₹{val/100000:.1f}L"
        if val >= 1000:
            return f"₹{val/1000:.0f}K"
        return f"₹{val:.0f}"

    return {
        "machines": {
            "title": "Total Machine Sell",
            "value": f"{machines_purchased}",
            "unit": "units",
            "subtitle": "Purchased by you",
            "icon": "cube-outline",
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
            "title": "Total Orders",
            "value": f"{total_received:02d}" if total_received > 0 else "0",
            "unit": "orders",
            "subtitle": f"Pending: {pending_orders_count:02d}",
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


# ✅ DISTRIBUTOR REPORTS DATA (Real Data Analytics)
@router.get("/reports-data")
def get_distributor_reports_data(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    user_id = current_user["user_id"]
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # Get total orders purchased overall
    total_qty_query = db.query(func.count(models.Order.id)).filter(
        models.Order.user_id == user_id
    ).scalar()
    total_qty = int(total_qty_query) if total_qty_query else 0

    # Get first order date to determine active period
    first_order = db.query(models.Order.order_date).filter(
        models.Order.user_id == user_id
    ).order_by(models.Order.order_date.asc()).first()

    if first_order:
        days = (datetime.utcnow() - first_order.order_date).days + 1
        months = ((datetime.utcnow().year - first_order.order_date.year) * 12 + datetime.utcnow().month - first_order.order_date.month) + 1
    else:
        days = 1
        months = 1

    # Calculate average daily and monthly purchases
    avg_daily_qty = round(total_qty / days, 2)
    avg_monthly_qty = round(total_qty / months, 1)

    # 3. Weekly Purchases (Last 7 days ending today)
    weekly_labels = []
    weekly_values = []
    
    for i in range(6, -1, -1):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_qty = db.query(func.count(models.Order.id)).filter(
            models.Order.user_id == user_id,
            models.Order.order_date >= day_start,
            models.Order.order_date < day_end
        ).scalar()
        weekly_labels.append(day_start.strftime('%a'))
        weekly_values.append(int(day_qty) if day_qty else 0)

    # 4. Monthly Discount Trend (Last 6 Months)
    monthly_discount_labels = []
    monthly_discount_values = []
    
    for i in range(5, -1, -1):
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
            
        m_start = datetime(target_year, target_month, 1)
        if target_month == 12:
            m_end = datetime(target_year + 1, 1, 1)
        else:
            m_end = datetime(target_year, target_month + 1, 1)
            
        discount_sum = db.query(func.sum(models.Order.discount_amount)).filter(
            models.Order.user_id == user_id,
            models.Order.order_date >= m_start,
            models.Order.order_date < m_end
        ).scalar()
        
        monthly_discount_labels.append(m_start.strftime('%b'))
        monthly_discount_values.append(float(discount_sum) if discount_sum else 0.0)

    # 5. Top Performing Products
    top_products_query = db.query(
        models.Order.product_id,
        func.count(models.Order.id).label('total_qty')
    ).filter(
        models.Order.user_id == user_id
    ).group_by(
        models.Order.product_id
    ).order_by(
        func.count(models.Order.id).desc()
    ).limit(3).all()
    
    top_products = []
    for item in top_products_query:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            top_products.append({
                "name": product.product_name,
                "sales": f"{item.total_qty} Units",
                "growth": "+10%"
            })
            
    if not top_products:
        top_products = [
            { "name": "No orders placed yet", "sales": "0 Units", "growth": "0%" }
        ]

    return {
        "daily_purchases": {
            "value": f"{avg_daily_qty} Units",
            "trend": "Avg. daily purchases"
        },
        "monthly_purchases": {
            "value": f"{avg_monthly_qty} Units",
            "trend": "Avg. monthly purchases"
        },
        "weekly_purchases_chart": {
            "labels": weekly_labels,
            "values": weekly_values
        },
        "discount_chart": {
            "labels": monthly_discount_labels,
            "values": monthly_discount_values
        },
        "top_products": top_products
    }

