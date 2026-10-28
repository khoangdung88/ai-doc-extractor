"""FastAPI application factory. Run: `uvicorn docext.api.app:create_app --factory`."""

from __future__ import annotations

from fastapi import FastAPI

from docext import __version__
from docext.api.errors import install_error_handlers
from docext.api.routes import extract, meta
from docext.core.config import get_settings
from docext.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, json=settings.env != "dev")
    app = FastAPI(
        title="docext",
        version=__version__,
        description="AI extraction of structured data from shipping documents.",
    )
    install_error_handlers(app)
    app.include_router(meta.router)
    app.include_router(extract.router, prefix="/v1")
    return app
