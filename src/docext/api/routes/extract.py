"""POST /v1/extract — multipart file + document type (+ optional model)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from docext.core.config import get_settings
from docext.core.errors import InputTooLargeError
from docext.extraction.pipeline import ExtractionResult
from docext.extraction.pipeline import extract as run_extraction
from docext.ingestion.registry import load_document

router = APIRouter(tags=["extraction"])


@router.post("/extract", response_model=ExtractionResult)
async def extract_document(
    file: Annotated[UploadFile, File(description="Document file (PDF)")],
    type: Annotated[str, Form(description="Document type, e.g. invoice")],
    model: Annotated[str | None, Form(description="<provider>:<model>")] = None,
) -> ExtractionResult:
    settings = get_settings()
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise InputTooLargeError(f"File exceeds {settings.max_upload_mb} MB")
    document = await load_document(data, file.filename, settings=settings)
    return await run_extraction(document, type, model, settings=settings)
