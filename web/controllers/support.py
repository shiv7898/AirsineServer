from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.database import SessionLocal
from schemas import SupportQueryCreate, SupportQueryResponse, SupportQueryResolve
from services.support_service import SupportService

router = APIRouter(tags=["Support"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/queries", response_model=SupportQueryResponse)
def create_query(query: SupportQueryCreate, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user
        return SupportService.create_query(
            db=db,
            user_id=current_user["user_id"],
            category=query.category,
            message=query.message,
            user_role=current_user.get("role"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/queries")
def get_all_queries(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] not in ["sub_admin", "super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return SupportService.get_all_queries(db)

@router.put("/admin/queries/{query_id}/resolve")
def resolve_query(query_id: int, payload: SupportQueryResolve, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] not in ["sub_admin", "super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return SupportService.resolve_query(db, query_id, payload.resolution_message)
