from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
import models
from schemas import SupportQueryCreate, UserCreate, UserLogin, UserResponse, ProductCreate, ProductResponse, OrderCreate, OrderResponse, ReferralCreate, TherapyCreate, MachineSettingsCreate
from auth import hash_password, verify_password, create_token, verify_token
import shutil, os
from datetime import datetime, timedelta
import pdfplumber
from exception import (
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
from validators import (
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
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# CORSMiddleware will be added after routers to ensure it runs first in the stack

from routers import products
from routers import auth_routes
from routers import orders
from routers import patient
from routers import doctor
from routers import distributor
from routers import report
from routers import admin
app.include_router(products.router)
app.include_router(auth_routes.router)
app.include_router(orders.router)
app.include_router(patient.router)
app.include_router(doctor.router)
app.include_router(distributor.router)
app.include_router(report.router)
app.include_router(admin.router)

# ✅ Auth Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    open_routes = ["/register", "/login", "/docs", "/openapi.json", "/products", "/redoc", "/admin/create-super-admin", "/uploads"]
    if request.method == "OPTIONS" or any(request.url.path.startswith(r) for r in open_routes):
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
        print(f"Token verification failed: {str(e)}")
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return verify_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Add CORS Middleware LAST so it executes FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

