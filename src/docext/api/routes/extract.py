"""POST /v1/extract — multipart file + optional document type (+ optional model).

Omit `type` to auto-detect document types per page (returns `AutoExtractionResult`)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from docext.core.config import get_settings
from docext.core.errors import InputTooLargeError
from docext.extraction.pipeline import AutoExtractionResult, ExtractionResult, extract_auto
from docext.extraction.pipeline import extract as run_extraction
from docext.extraction.providers.registry import CREDENTIAL_SETTINGS, resolve_model
from docext.ingestion.registry import load_document

router = APIRouter(tags=["extraction"])


@router.post("/extract", response_model=ExtractionResult | AutoExtractionResult)
async def extract_document(
    file: Annotated[UploadFile, File(description="Document file (PDF)")],
    type: Annotated[
        str | None, Form(description="Document type, e.g. invoice; omit to auto-detect")
    ] = None,
    model: Annotated[str | None, Form(description="<provider>:<model>")] = None,
    api_key: Annotated[
        str | None, Form(description="Provider API key override (this request only)")
    ] = None,
) -> ExtractionResult | AutoExtractionResult:
    settings = get_settings()
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise InputTooLargeError(f"File exceeds {settings.max_upload_mb} MB")
    document = await load_document(data, file.filename, settings=settings)

    provider_name, _ = resolve_model(model or settings.default_model)
    if api_key and (field := CREDENTIAL_SETTINGS.get(provider_name)):
        settings = settings.model_copy(update={field: api_key})

    if type is None:
        return await extract_auto(document, model, settings=settings)
    return await run_extraction(document, type, model, settings=settings)
