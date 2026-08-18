from core.security import verify_token
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import SessionLocal
import models
import os, shutil
from datetime import datetime, timedelta, date
from helpers.utils import paginate
from schemas import OrderCreate, OrderResponse, ProductResponse
from typing import List, Optional
import json
from services.product_service import ProductService

router = APIRouter(tags=["Distributor"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def distributor_section(request: Request, db: Session = Depends(get_db)):
    user = request.state.user

    if user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    db_user = db.query(models.Distributor).filter(
        models.Distributor.id == user["user_id"]
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

@router.get("/orders")
def distributor_orders(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

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

@router.get("/dashboard")
def distributor_dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    orders_query = db.query(models.Order).join(models.Product).filter(
        models.Product.distributor_id == current_user["user_id"]
    )
    
    total_orders = orders_query.count()
    confirmed = orders_query.filter(models.Order.status == 1).count()
    pending = orders_query.filter(models.Order.status == 0).count()
    delivered = orders_query.filter(models.Order.status == 2).count()

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

@router.put("/update-product/{product_id}", response_model=ProductResponse)
def update_product_distributor(
    product_id: int,
    product_name: str = Form(...),
    product_type: str = Form(...),
    unit_price: float = Form(0.0),
    unit_mrp: float = Form(...),
    discount: float = Form(0.0),
    description: str = Form(None),
    brand: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    selling_price: Optional[float] = Form(None),
    referral_discount: float = Form(0.0),
    tax_gst: Optional[float] = Form(None),
    stock_pieces: int = Form(0),
    product_status: str = Form("Active"),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            current_user = verify_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        role = current_user.get("role")
        if role == "distributor":
            product = db.query(models.Product).filter(
                models.Product.id == product_id,
                models.Product.distributor_id == current_user.get("user_id")
            ).first()
        elif role in ["admin", "super_admin"]:
            product = db.query(models.Product).filter(
                models.Product.id == product_id
            ).first()
        else:
            raise HTTPException(status_code=403, detail="Not authorized.")

        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not owned by you.")

        image_filenames = []
        if product.product_images:
            try:
                image_filenames = json.loads(product.product_images)
            except:
                pass

        if images and len(images) > 0 and images[0].filename:
            os.makedirs("uploads/products", exist_ok=True)
            for img in images:
                if img.filename:
                    extension = img.filename.split(".")[-1]
                    img_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{extension}"
                    image_path = f"uploads/products/{img_name}"
                    with open(image_path, "wb") as buffer:
                        shutil.copyfileobj(img.file, buffer)
                    image_filenames.append(img_name)
                    
        if selling_price is None:
            selling_price = unit_mrp - (unit_mrp * discount / 100.0)

        product_images_json = json.dumps(image_filenames) if image_filenames else None
        image_filename = image_filenames[0] if image_filenames else None

        product.product_name = product_name
        product.product_type = product_type
        product.unit_price = unit_price
        product.unit_mrp = unit_mrp
        product.discount = discount
        product.description = description
        product.brand = brand
        product.model_name = model_name
        product.selling_price = selling_price
        product.referral_discount = referral_discount
        product.tax_gst = tax_gst if tax_gst is not None else product.tax_gst
        product.stock_pieces = stock_pieces
        product.product_status = product_status
        product.product_images = product_images_json
        if image_filename:
            product.product_image = image_filename

        db.commit()
        db.refresh(product)
        return product
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
        models.Product.target_audience == "distributor",
        models.Product.is_available == True
    )

    products_data = paginate(query, page=page, limit=limit)

    for product in products_data["data"]:
        if product.product_image:
            product.image_url = f"{request.base_url}uploads/products/{product.product_image}"
        else:
            product.image_url = None

    return products_data

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
        product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        total = product.unit_price * order.quantity
        discount_amount = 0
        final_amount = total

        if order.referral_code:
            referral_user = db.query(models.Patient).filter(models.Patient.referral_code == order.referral_code).first() or db.query(models.Doctor).filter(models.Doctor.referral_code == order.referral_code).first()
            if referral_user:
                discount_amount = total * 0.10
                final_amount = total - discount_amount

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
            status=0
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # Set formatted order_number
        new_order.order_number = f"#ORD-{new_order.id:04d}"
        db.commit()

        return {
            "message": "Order placed successfully",
            "order_id": new_order.id,
            "order_number": new_order.order_number,
            "status": "PENDING"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/summary")
def get_distributor_summary(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    orders_query = db.query(models.Order).filter(
        models.Order.user_id == current_user["user_id"]
    )
    
    total_received = orders_query.count()
    revenue = sum([
        o.total_amount for o in orders_query.all()
        if o.status != 0 and o.total_amount is not None
    ])
    profit = revenue * 0.20
    pending_orders_count = orders_query.filter(models.Order.status == 0).count()

    pending_queries = db.query(models.Notification).filter(
        models.Notification.user_id == current_user["user_id"],
        models.Notification.title.like("Support Query%"),
        models.Notification.is_read == False
    ).count()

    machines_purchased = orders_query.count()

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

@router.post("/support-query")
def distributor_support_query(
    request: Request,
    category: str = Form(...),
    message: str = Form(...),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        user_db = db.query(models.Distributor).filter(models.Distributor.id == current_user["user_id"]).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="Distributor not found")

        image_filenames = []
        os.makedirs("uploads/support", exist_ok=True)

        if images:
            for img in images:
                if img.filename:
                    img_filename = f"supp_{current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{img.filename}"
                    image_path = f"uploads/support/{img_filename}"
                    with open(image_path, "wb") as buffer:
                        shutil.copyfileobj(img.file, buffer)
                    image_filenames.append(img_filename)
        
        image_filename_str = ",".join(image_filenames) if image_filenames else None

        new_query = models.SupportQuery(
            user_id=current_user["user_id"],
            query_type=category,
            message=message,
            image=image_filename_str,
            status="pending"
        )

        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        
        return {"message": "Query submitted successfully", "query_id": new_query.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports-data")
def get_distributor_reports_data(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] != "distributor":
        raise HTTPException(status_code=403, detail="Access denied")

    user_id = current_user["user_id"]
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    total_qty_query = db.query(func.count(models.Order.id)).filter(
        models.Order.user_id == user_id
    ).scalar()
    total_qty = int(total_qty_query) if total_qty_query else 0

    first_order = db.query(models.Order.order_date).filter(
        models.Order.user_id == user_id
    ).order_by(models.Order.order_date.asc()).first()

    if first_order:
        days = (datetime.utcnow() - first_order.order_date).days + 1
        months = ((datetime.utcnow().year - first_order.order_date.year) * 12 + datetime.utcnow().month - first_order.order_date.month) + 1
    else:
        days = 1
        months = 1

    avg_daily_qty = round(total_qty / days, 2)
    avg_monthly_qty = round(total_qty / months, 1)

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

@router.post("/add-product", response_model=ProductResponse)
def add_product(
    request: Request,
    product_name: str = Form(...),
    product_type: str = Form(...),
    unit_price: float = Form(0.0),
    unit_mrp: float = Form(...),
    discount: float = Form(0.0),
    description: str = Form(None),
    brand: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    selling_price: Optional[float] = Form(None),
    referral_discount: float = Form(0.0),
    tax_gst: Optional[float] = Form(None),
    stock_pieces: int = Form(0),
    product_status: str = Form("Active"),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    if current_user.get("role") != "super_admin":
        user_db = db.query(models.AdminStaff).filter(
            models.AdminStaff.id == current_user.get("user_id")
        ).first()
        if not user_db:
            raise HTTPException(status_code=403, detail="Admin staff not found")

        perms_str = user_db.permissions or "{}"
        has_permission = False
        try:
            perms_dict = json.loads(perms_str)
            products_perms = perms_dict.get("products", [])
            if isinstance(products_perms, list) and ("create" in products_perms or "edit" in products_perms):
                has_permission = True
        except Exception:
            pass

        if "create_product" in perms_str or "manage_products" in perms_str:
            has_permission = True

        if not has_permission:
            raise HTTPException(status_code=403, detail="Not authorized. 'products:create' permission required.")

    try:
        return ProductService.create_product(
            db=db,
            product_name=product_name,
            product_type=product_type,
            unit_mrp=unit_mrp,
            unit_price=unit_price,
            discount=discount,
            description=description,
            brand=brand,
            model_name=model_name,
            selling_price=selling_price,
            referral_discount=referral_discount,
            tax_gst=tax_gst,
            stock_pieces=stock_pieces,
            product_status=product_status,
            target_audience="distributor",
            images=images if images else [],
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
