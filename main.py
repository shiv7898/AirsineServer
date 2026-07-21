from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine, Base
import app.models as models
from app.schemas import SupportQueryCreate, UserCreate, UserLogin, UserResponse, ProductCreate, ProductResponse, OrderCreate, OrderResponse, ReferralCreate, TherapyCreate, MachineSettingsCreate
from app.core.auth import hash_password, verify_password, create_token, verify_token
import shutil, os
from datetime import datetime, timedelta
import pdfplumber
from app.core.exception import (
    AppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    DatabaseException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from helpers.validators import (
    validate_email,
    validate_password,
    validate_phone,
    validate_pincode,
    validate_age,
    validate_role
)
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:  
            text += page.extract_text() or ""
    return text
import re
def parse_therapy_data(text):
    import re

    # match: 4.4h 57.1% 0.8 14.4 174.3
    match = re.search(
        r"(\d+\.?\d*)h\s+(\d+\.?\d*)%\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
        text
    )

    if match:
        data = {
            "usage_time": match.group(1),
            "compliance": match.group(2),
            "ahi_index": match.group(3),
            "avg_pressure": match.group(4),
            "leak_rate": match.group(5),
        }
        print("===== PARSED DATA =====")
        print(data)
        return data

    print("===== NO MATCH FOUND =====")
    return {
        "usage_time": None,
        "compliance": None,
        "ahi_index": None,
        "avg_pressure": None,
        "leak_rate": None,
    }
Base.metadata.create_all(bind=engine)

# Auto migrate products table
try:
    with engine.begin() as conn:
        from sqlalchemy import text
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='target_audience';"))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE products ADD COLUMN target_audience VARCHAR DEFAULT 'patient_doctor';"))
            print("Successfully added target_audience to products table")
except Exception as e:
    print(f"Migration error: {e}")

app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/admin-ui", StaticFiles(directory="web/statics/admin"), name="admin-ui")

# Web routes are now in web/routes.py

@app.get("/")
async def root():
    return {"message": "Welcome to Airsine"}

# CORSMiddleware will be added after routers to ensure it runs first in the stack

from app.api.router import api_router
from web.routes import router as web_router

app.include_router(api_router)
app.include_router(web_router)

# ✅ Auth Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    open_routes = [
        "/web/user/login", "/web/user/register",
        "/web/auth/login",
        "/mobile/user/login", "/mobile/user/register",
        "/mobile/products",
        "/login", "/register", "/openapi.json", "/products", 
        "/redoc", "/create-super-admin", "/uploads", 
        "/admin-dashboard", "/admin-ui", "/favicon.ico",
        "/dashboard", "/users", "/admin-staff", "/distributors", "/create-staff", "/create-user", "/create-product",
        "/products-admin", "/orders-admin", "/queries-admin", "/profile", "/.well-known", "/api/test-db",
        "/user-view", "/user-edit",
        "/staff-view", "/staff-edit",
        "/distributor-view", "/distributor-edit",
        "/docs"
    ]
    if request.method == "OPTIONS" or request.url.path == "/" or any(request.url.path.startswith(r) for r in open_routes):
        return await call_next(request)
    
    token = request.headers.get("Authorization")
    print(f"===== AUTH DEBUG =====")
    print(f"Path: {request.url.path}")
    print(f"Authorization Header: {token}")
    
    if not token or not token.startswith("Bearer "):
        print("Token missing or invalid format")
        return JSONResponse(status_code=401, content={"detail": "Token missing"})
    
    try:
        token_data = verify_token(token.split(" ")[1])
        print(f"Token verified: {token_data}")
        request.state.user = token_data
    except Exception as e:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})
    
    return await call_next(request)

# ✅ Swagger Authorize Button
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title="Airsine Hospital API", version="1.0.0", routes=app.routes)
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer"}
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="web/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise AuthorizationException(f"Invalid token: {str(e)}")

@app.get("/api/test-db")
def test_db(db: Session = Depends(get_db)):
    from fastapi.responses import JSONResponse
    u = db.query(models.User).filter(models.User.id == 6).first()
    if u:
        return JSONResponse({"id": u.id, "name": u.name, "phone": u.phone, "age": u.age, "gender": u.gender, "address": u.home_address})
    return JSONResponse({"error": "not found"})

# ✅ Add CORS Middleware LAST so it executes FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

