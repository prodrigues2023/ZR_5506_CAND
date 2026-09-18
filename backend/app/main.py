"""FastAPI application factory and process entry point."""

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.application.exceptions import ApplicationError, ResourceNotFound
from app.config import get_settings
from app.presentation.comments import router as comments_router
from app.presentation.episodes import router as episodes_router
from app.presentation.health import router as health_router
from app.presentation.insights import router as insights_router
from app.presentation.series import router as series_router


def create_app() -> FastAPI:
    """Build the API application with its infrastructure adapters."""

    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(ApplicationError)
    async def handle_application_error(_: Request, exception: ApplicationError) -> JSONResponse:
        status_code = 404 if isinstance(exception, ResourceNotFound) else 400
        return JSONResponse(status_code=status_code, content={"detail": str(exception)})

    @application.exception_handler(httpx.HTTPError)
    async def handle_provider_error(_: Request, __: httpx.HTTPError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": "External provider unavailable"})

    application.include_router(health_router, prefix="/api")
    application.include_router(series_router, prefix="/api")
    application.include_router(episodes_router, prefix="/api")
    application.include_router(comments_router, prefix="/api")
    application.include_router(insights_router, prefix="/api")
    return application


app = create_app()
