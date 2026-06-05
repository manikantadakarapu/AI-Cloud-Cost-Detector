from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_routes import router as health_router
from app.api.v1.router import api_router
from app.core.auth import azure_scheme
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.websockets.progress import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if azure_scheme.app_client_id:
        await azure_scheme.openid_config.load_config()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    
    swagger_ui_init_oauth = None
    if settings.azure_openapi_client_id:
        swagger_ui_init_oauth = {
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": settings.azure_openapi_client_id,
        }

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Backend foundation for an AI-powered Azure FinOps platform.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_oauth2_redirect_url="/oauth2-redirect",
        swagger_ui_init_oauth=swagger_ui_init_oauth,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(websocket_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    return app


app = create_app()
