"""Explicit loader registry and the single entry point `load_document`."""

from __future__ import annotations

from docext.core.config import Settings, get_settings
from docext.core.errors import InputTooLargeError, UnsupportedFormatError
from docext.ingestion.base import Document, Loader
from docext.ingestion.detect import detect_mime
from docext.ingestion.pdf import PdfLoader

LOADERS: list[Loader] = [PdfLoader()]


def get_loader(mime_type: str, filename: str | None = None) -> Loader:
    for loader in LOADERS:
        if loader.supports(mime_type, filename):
            return loader
    raise UnsupportedFormatError(
        f"No loader for '{mime_type}'",
        details={"supported": [loader.name for loader in LOADERS]},
    )


async def load_document(
    data: bytes, filename: str | None = None, *, settings: Settings | None = None
) -> Document:
    settings = settings or get_settings()
    if len(data) > settings.max_upload_bytes:
        raise InputTooLargeError(
            f"File exceeds {settings.max_upload_mb} MB",
            details={"size_bytes": len(data), "max_mb": settings.max_upload_mb},
        )
    mime = detect_mime(data, filename)
    return await get_loader(mime, filename).load(data, filename)
