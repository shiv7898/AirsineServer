from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import SupportQueryCreate, SupportQueryResponse

# Create router
router = APIRouter(
    prefix="/support",
    tags=["Support Queries"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ SUBMIT A QUERY
@router.post("/queries", response_model=SupportQueryResponse)
def create_query(query: SupportQueryCreate, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user

        new_query = models.SupportQuery(
            user_id=current_user["user_id"],
            query_type=query.category,
            message=query.message,
            status="pending"
        )
        
        db.add(new_query)
        db.commit()
        db.refresh(new_query)

        return new_query

    except Exception as e:
        import traceback
        print("CREATE QUERY ERROR:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ✅ ADMIN GET ALL QUERIES
@router.get("/admin/queries")
def get_all_queries(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    # Basic role check, or you can import check_admin_permission
    if current_user["role"] not in ["sub_admin", "super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    queries = db.query(models.SupportQuery).order_by(models.SupportQuery.created_at.desc()).all()
    
    result = []
    for q in queries:
        user = db.query(models.User).filter(models.User.id == q.user_id).first()
        result.append({
            "id": q.id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "user_role": user.role if user else "Unknown",
            "query_type": q.query_type,
            "message": q.message,
            "status": q.status,
            "created_at": q.created_at
        })
        
    return result

# ✅ ADMIN RESOLVE QUERY
@router.put("/admin/queries/{query_id}/resolve")
def resolve_query(query_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] not in ["sub_admin", "super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(models.SupportQuery).filter(models.SupportQuery.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
        
    query.status = "resolved"
    db.commit()
    
    return {"message": "Query resolved successfully", "query_id": query_id}
