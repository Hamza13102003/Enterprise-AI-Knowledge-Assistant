import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.constants import API_TITLE, API_V1_PREFIX, API_VERSION
from app.core.settings import settings
from app.exceptions.handlers import register_exception_handlers
from app.observability.logging_config import setup_logging
from app.schemas.api_response import APIResponse
from app.utils.response import success_response

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    setup_logging()

    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Production-inspired Enterprise AI Knowledge Assistant",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["Root"], response_model=APIResponse)
    async def root() -> APIResponse:
        """
        Root endpoint.
        """
        return success_response(
            message="Application is running",
            data={
                "application": settings.app_name,
                "environment": settings.app_env,
                "version": API_VERSION,
                "docs": "/docs",
            },
        )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=API_V1_PREFIX)

    logger.info("Application created successfully")

    return app
