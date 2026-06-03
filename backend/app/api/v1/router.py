from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.api.v1.analysis_routes import router as analysis_router
from app.api.v1.subscription_routes import router as subscription_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.admin_routes import router as admin_router
from app.api.v1.tenant_routes import router as tenant_router

api_router = APIRouter(dependencies=[Depends(get_current_user)])
api_router.include_router(user_router, tags=["users"])
api_router.include_router(admin_router)
api_router.include_router(subscription_router)
api_router.include_router(analysis_router)
api_router.include_router(tenant_router)
