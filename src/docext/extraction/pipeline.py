"""The extraction pipeline: Document + document type + model → validated `ExtractionResult`.

This module must never branch on a concrete document type, provider, or input format.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from docext.core.config import Settings, get_settings
from docext.core.errors import ExtractionValidationError, InputTooLargeError
from docext.core.logging import get_logger
from docext.domain.registry import get_document_type
from docext.extraction.json_repair import parse_json_output
from docext.extraction.prompts.loader import load_prompt
from docext.extraction.providers.base import ExtractionRequest, ModelProvider, Usage
from docext.extraction.providers.registry import create_provider, resolve_model
from docext.ingestion.base import Document

log = get_logger(__name__)


class ExtractionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    document_type: str
    schema_version: str
    model: str
    prompt_version: str
    data: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)
    latency_ms: int = 0
    pages: int = 0
    source_name: str | None = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


async def extract(
    document: Document,
    document_type: str,
    model: str | None = None,
    *,
    settings: Settings | None = None,
    provider: ModelProvider | None = None,
) -> ExtractionResult:
    """Run one extraction. Pass `provider` to reuse a client (tests, batch); else one is created."""
    settings = settings or get_settings()
    doc_type = get_document_type(document_type)
    spec = model or settings.default_model
    provider_name, model_name = resolve_model(spec)

    text = document.text
    if len(text) > settings.max_input_chars:
        raise InputTooLargeError(
            f"Document text exceeds {settings.max_input_chars} characters",
            details={"chars": len(text)},
        )

    schema = doc_type.schema.json_schema_for_prompt()
    template = load_prompt(doc_type.name, doc_type.prompt_version)
    system_prompt, user_prompt = template.render(
        schema_json=json.dumps(schema, indent=2),
        document_text=text,
        today=datetime.now(UTC).date().isoformat(),
    )
    request = ExtractionRequest(
        model=model_name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_schema=schema,
        document_type=doc_type.name,
        source_name=document.filename,
        images_png=[p.image_png for p in document.pages if p.image_png is not None],
    )

    owned = provider is None
    provider = provider or create_provider(provider_name, settings)
    started = time.perf_counter()
    try:
        response = await provider.extract_structured(request)
        parsed = parse_json_output(response.raw_json)
        try:
            instance = doc_type.schema.model_validate(parsed)
        except ValidationError as exc:
            raise ExtractionValidationError(
                "Model output does not match schema",
                details={"errors": exc.errors(include_url=False)},
            ) from exc
    except Exception as exc:
        log.warning(
            "extraction_failed",
            doc_type=doc_type.name,
            model=spec,
            error=type(exc).__name__,
            ms=int((time.perf_counter() - started) * 1000),
        )
        raise
    finally:
        if owned:
            await provider.close()

    result = ExtractionResult(
        document_type=doc_type.name,
        schema_version=instance.schema_version,
        model=response.model,
        prompt_version=template.version,
        data=instance.model_dump(mode="json"),
        warnings=instance.warnings(),
        usage=response.usage,
        latency_ms=response.latency_ms,
        pages=len(document.pages),
        source_name=document.filename,
    )
    log.info(
        "extraction_completed",
        doc_type=result.document_type,
        model=result.model,
        prompt_version=result.prompt_version,
        input_tokens=result.usage.input_tokens,
        output_tokens=result.usage.output_tokens,
        ms=result.latency_ms,
        warnings=len(result.warnings),
    )
    return result
