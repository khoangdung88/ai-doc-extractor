"""Single place mapping `DocextError` to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from docext.core.errors import DocextError


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DocextError)
    async def _handle(_: Request, exc: DocextError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )
