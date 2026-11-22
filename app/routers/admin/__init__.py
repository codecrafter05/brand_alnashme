from fastapi import APIRouter

from . import auth, categories, dashboard, delivery, orders, products, settings

router = APIRouter()
router.include_router(dashboard.router)  # carries its own /admin prefix (path "")
for module in (auth, categories, products, delivery, orders, settings):
    router.include_router(module.router, prefix="/admin")
