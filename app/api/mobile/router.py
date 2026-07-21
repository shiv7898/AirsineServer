from fastapi import APIRouter

from app.api.mobile.auth import router as auth_router
from app.api.mobile.patient import router as patient_router
from app.api.mobile.doctor import router as doctor_router
from app.api.mobile.distributor import router as distributor_router
from app.api.mobile.products import router as products_router

mobile_router = APIRouter()

mobile_router.include_router(auth_router, prefix="/user")
mobile_router.include_router(patient_router, prefix="/patient")
mobile_router.include_router(doctor_router, prefix="/doctor")
mobile_router.include_router(distributor_router, prefix="/distributor")
mobile_router.include_router(products_router, prefix="/products")
