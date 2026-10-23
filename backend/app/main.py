"""Application factory for the ScholarCheck API (S01 T01).

Run in development:
    cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, opportunities
from app.api.errors import register_exception_handlers
from app.config import Settings, load_settings

API_PREFIX = "/api"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the ASGI app. ``settings`` is injectable for tests."""

    resolved = settings or load_settings()
    app = FastAPI(
        title="ScholarCheck API",
        summary="Evidence-backed scholarship decisions.",
        version="0.1.0",
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.state.settings = resolved
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    register_exception_handlers(app)
    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(opportunities.router, prefix=API_PREFIX)
    return app


app = create_app()
