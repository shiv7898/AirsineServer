"""
services/order_service.py

Centralized order business logic.
Handles order creation, status updates, and fetching for
both Web API and Mobile API.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

import models


class OrderService:

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_referral_discount(
        db: Session,
        base_amount: float,
        referral_code: Optional[str],
        user_role: str,
        product: models.Product,
    ) -> float:
        """Calculate referral discount amount given a code and user role using product's discount."""
        if not referral_code:
            return 0.0

        # Check custom referral codes table first
        referral = db.query(models.ReferralCode).filter(
            models.ReferralCode.code == referral_code,
            models.ReferralCode.is_active == True,
            models.ReferralCode.role == user_role,
        ).first()

        # Fallback: user's personal referral code
        referral_user = (
            db.query(models.Patient).filter(models.Patient.referral_code == referral_code).first()
            or db.query(models.Doctor).filter(models.Doctor.referral_code == referral_code).first()
            or db.query(models.Distributor).filter(models.Distributor.referral_code == referral_code).first()
        )

        if referral or referral_user:
            if referral:
                referral.used_count = (referral.used_count or 0) + 1
            pct = product.referral_discount or 0.0
            return base_amount * (pct / 100.0)

        return 0.0

    # ------------------------------------------------------------------
    # CREATE ORDER
    # ------------------------------------------------------------------

    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        user_role: str,
        product_id: int,
        quantity: int,
        customer_name: str,
        customer_phone: str,
        building: Optional[str] = None,
        locality: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        referral_code: Optional[str] = None,
    ) -> models.Order:
        """Create a new order with discount and referral calculations."""

        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Price calculation
        unit_price = product.selling_price or product.unit_mrp or product.unit_price
        total = unit_price * quantity

        # Customer discount
        cust_discount_pct = product.customer_discount or 0.0
        product_discount_amount = total * (cust_discount_pct / 100.0)
        discounted_base = total - product_discount_amount

        # Referral discount
        referral_discount_amount = OrderService._calculate_referral_discount(
            db, discounted_base, referral_code, user_role, product
        )

        final_amount_before_tax = discounted_base - referral_discount_amount
        total_discount = product_discount_amount + referral_discount_amount
        
        # GST
        gst_pct = product.tax_gst or 0.0
        gst_amount = final_amount_before_tax * (gst_pct / 100.0)
        final_amount = final_amount_before_tax + gst_amount

        new_order = models.Order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            referral_code=referral_code,
            customer_name=customer_name,
            customer_phone=str(customer_phone),
            total_amount=total,
            discount_amount=total_discount,
            final_amount=final_amount,
            mrp_amount=(product.unit_mrp or unit_price) * quantity,
            mrp_discount_amount=max(0, ((product.unit_mrp or unit_price) * quantity) - total),
            product_discount_amount=product_discount_amount,
            referral_discount_amount=referral_discount_amount,
            gst_amount=gst_amount,
            currency="INR",
            building=building,
            locality=locality,
            district=district,
            state=state,
            pincode=str(pincode) if pincode else None,
            user_role=user_role,
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # Set formatted order_number
        new_order.order_number = f"#ORD-{new_order.id:04d}"
        db.commit()
        db.refresh(new_order)

        return new_order

    # ------------------------------------------------------------------
    # GET ORDERS
    # ------------------------------------------------------------------

    @staticmethod
    def get_all_orders(db: Session) -> List[models.Order]:
        """Fetch all orders (for admin view)."""
        return db.query(models.Order).order_by(models.Order.id.desc()).all()

    @staticmethod
    def get_orders_by_user(db: Session, user_id: int) -> List[models.Order]:
        """Fetch orders for a specific user."""
        return (
            db.query(models.Order)
            .filter(models.Order.user_id == user_id)
            .order_by(models.Order.id.desc())
            .all()
        )

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> models.Order:
        """Fetch a single order by ID."""
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    # ------------------------------------------------------------------
    # UPDATE ORDER STATUS
    # ------------------------------------------------------------------

    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str) -> models.Order:
        """Update an order's status (PENDING → APPROVED → DELIVERED)."""
        valid_statuses = {"PENDING", "APPROVED", "DELIVERED", "CANCELLED"}
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        order = OrderService.get_order_by_id(db, order_id)
        order.status = status
        db.commit()
        db.refresh(order)
        return order
