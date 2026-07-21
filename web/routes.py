from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="web/templates")

@router.get("/admin-dashboard", include_in_schema=False)
@router.get("/dashboard", include_in_schema=False)
@router.get("/users", include_in_schema=False)
@router.get("/admin-staff", include_in_schema=False)
@router.get("/distributors", include_in_schema=False)
@router.get("/create-staff", include_in_schema=False)
@router.get("/create-user", include_in_schema=False)
@router.get("/create-product", include_in_schema=False)
@router.get("/products-admin", include_in_schema=False)
@router.get("/orders-admin", include_in_schema=False)
@router.get("/queries-admin", include_in_schema=False)
@router.get("/profile", include_in_schema=False)
@router.get("/login", include_in_schema=False)
@router.get("/user-view/{user_id}", include_in_schema=False)
@router.get("/user-edit/{user_id}", response_class=HTMLResponse, include_in_schema=False)
@router.get("/staff-view/{user_id}", include_in_schema=False)
@router.get("/staff-edit/{user_id}", response_class=HTMLResponse, include_in_schema=False)
@router.get("/distributor-view/{user_id}", include_in_schema=False)
@router.get("/distributor-edit/{user_id}", response_class=HTMLResponse, include_in_schema=False)
async def serve_admin_dashboard(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
