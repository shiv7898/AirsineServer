from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from web.controllers.auth import router as auth_router, login, get_db
from web.controllers.admin import router as admin_router
from web.controllers.products import router as products_router
from web.controllers.orders import router as orders_router
from web.controllers.support import router as support_router
from web.controllers.report import router as report_router
from schemas import UserLogin

web_router = APIRouter()

web_router.include_router(auth_router, prefix="/user")
web_router.include_router(admin_router, prefix="/admin")
web_router.include_router(products_router, prefix="/products")
web_router.include_router(orders_router, prefix="/orders")
web_router.include_router(support_router, prefix="/support")
web_router.include_router(report_router, prefix="/report")

@web_router.post("/auth/login")
def fallback_login(user: UserLogin, db: Session = Depends(get_db)):
    return login(user, db)
