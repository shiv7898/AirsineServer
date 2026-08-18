from fastapi import APIRouter

from web.router import web_router as web_api_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.patient import router as patient_router
from api.v1.endpoints.doctor import router as doctor_router
from api.v1.endpoints.distributor import router as distributor_router
from api.v1.endpoints.products import router as products_router
from api.v1.endpoints.orders import router as orders_router

mobile_v1_router = APIRouter()

mobile_v1_router.include_router(auth_router, prefix="/user")
mobile_v1_router.include_router(patient_router, prefix="/patient")
mobile_v1_router.include_router(doctor_router, prefix="/doctor")
mobile_v1_router.include_router(distributor_router, prefix="/distributor")
mobile_v1_router.include_router(products_router, prefix="/products")
mobile_v1_router.include_router(orders_router, prefix="/orders")

api_router = APIRouter()
api_router.include_router(web_api_router, prefix="/api/v1/web")
api_router.include_router(mobile_v1_router, prefix="/api/v1/mobile")
