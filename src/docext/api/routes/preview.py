"""POST /v1/preview — per-page document text for the review UI (spec 0006).

Ingestion only, no model call: returns the same text layer the pipeline would feed to a
model, so reviewers compare extracted values against what the model actually saw."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from docext.core.config import get_settings
from docext.core.errors import InputTooLargeError
from docext.ingestion.registry import load_document

router = APIRouter(tags=["preview"])


class PreviewPage(BaseModel):
    number: int
    text: str


class DocumentPreview(BaseModel):
    filename: str | None
    mime_type: str
    pages: list[PreviewPage]


@router.post("/preview", response_model=DocumentPreview)
async def preview_document(
    file: Annotated[UploadFile, File(description="Document file (PDF)")],
) -> DocumentPreview:
    settings = get_settings()
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise InputTooLargeError(f"File exceeds {settings.max_upload_mb} MB")
    document = await load_document(data, file.filename, settings=settings)
    return DocumentPreview(
        filename=document.filename,
        mime_type=document.mime_type,
        pages=[PreviewPage(number=p.number, text=p.text) for p in document.pages],
    )
