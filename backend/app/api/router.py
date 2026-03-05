from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.services import router as services_router
from app.api.routes.customers import router as customers_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.quotes import router as quotes_router
from app.api.routes.returns import router as returns_router
from app.api.routes.marketplace import router as marketplace_router
from app.api.routes.kiwify import router as kiwify_router
from app.api.routes.service_marketplace import router as service_marketplace_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(services_router)
api_router.include_router(customers_router)
api_router.include_router(vehicles_router)
api_router.include_router(dashboard_router)
api_router.include_router(quotes_router)
api_router.include_router(returns_router)
api_router.include_router(marketplace_router)
api_router.include_router(kiwify_router)
api_router.include_router(service_marketplace_router)