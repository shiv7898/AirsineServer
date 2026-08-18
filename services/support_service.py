"""
services/support_service.py

Centralized support query business logic.
Handles query creation and admin retrieval/resolution.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

import models


class SupportService:

    # ------------------------------------------------------------------
    # RESOLVE USER FROM QUERY
    # ------------------------------------------------------------------

    @staticmethod
    def _find_user(db: Session, user_id: int, user_role: Optional[str] = None):
        """Look up the user who submitted a support query, across all tables."""
        # Fast path: use stored role if available
        role_model_map = {
            "patient": models.Patient,
            "doctor": models.Doctor,
            "distributor": models.Distributor,
            "admin": models.AdminStaff,
            "sub_admin": models.AdminStaff,
            "super_admin": models.SuperAdmin,
        }
        if user_role and user_role in role_model_map:
            model = role_model_map[user_role]
            user = db.query(model).filter(model.id == user_id).first()
            if user:
                return user

        # Fallback: search all tables
        for model in [
            models.Patient, models.Doctor, models.Distributor,
            models.AdminStaff, models.SuperAdmin,
        ]:
            user = db.query(model).filter(model.id == user_id).first()
            if user:
                return user
        return None

    # ------------------------------------------------------------------
    # CREATE QUERY
    # ------------------------------------------------------------------

    @staticmethod
    def create_query(
        db: Session,
        user_id: int,
        category: str,
        message: str,
        user_role: Optional[str] = None,
    ) -> models.SupportQuery:
        """Save a new support query from a user."""
        new_query = models.SupportQuery(
            user_id=user_id,
            query_type=category,
            message=message,
            status="pending",
            user_role=user_role,
        )
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return new_query

    # ------------------------------------------------------------------
    # GET ALL QUERIES (Admin)
    # ------------------------------------------------------------------

    @staticmethod
    def get_all_queries(db: Session) -> List[dict]:
        """Fetch all support queries with resolved user info."""
        queries = (
            db.query(models.SupportQuery)
            .order_by(models.SupportQuery.created_at.desc())
            .all()
        )

        result = []
        for q in queries:
            user_role = getattr(q, "user_role", None)
            user = SupportService._find_user(db, q.user_id, user_role)
            result.append({
                "id": q.id,
                "user_name": user.name if user else "Unknown",
                "user_email": user.email if user else "Unknown",
                "user_role": user.role if user else "Unknown",
                "query_type": q.query_type,
                "message": q.message,
                "status": q.status,
                "image": q.image,
                "created_at": q.created_at,
                "resolution_message": q.resolution_message,
                "resolved_at": q.resolved_at,
            })

        return result

    # ------------------------------------------------------------------
    # RESOLVE QUERY (Admin)
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_query(db: Session, query_id: int, resolution_message: Optional[str] = None) -> dict:
        """Mark a support query as resolved."""
        query = db.query(models.SupportQuery).filter(
            models.SupportQuery.id == query_id
        ).first()
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")

        query.status = "resolved"
        query.resolved_at = datetime.utcnow()
        if resolution_message:
            query.resolution_message = resolution_message
        db.commit()
        return {"message": "Query resolved successfully", "query_id": query_id}
