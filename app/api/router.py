from fastapi import APIRouter

from web.router import web_router as web_api_router
from app.api.mobile.router import mobile_router as mobile_api_router

api_router = APIRouter()

api_router.include_router(web_api_router, prefix="/web")
api_router.include_router(mobile_api_router, prefix="/mobile")
