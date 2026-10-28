"""Page-level document-type detection for combined PDFs (see spec 0004 / ADR-0007).

One provider call labels every page with a registry type name or `unknown`. Model output is
untrusted: unregistered labels and missing/out-of-range pages are coerced to `unknown` so a
confused model can never fabricate a type or drop the file silently.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from docext.core.config import Settings, get_settings
from docext.core.errors import ClassificationError, ExtractionValidationError
from docext.core.logging import get_logger
from docext.domain.registry import DOCUMENT_TYPES, list_document_types
from docext.extraction.json_repair import parse_json_output
from docext.extraction.prompts.loader import load_prompt
from docext.extraction.providers.base import ExtractionRequest, ModelProvider
from docext.ingestion.base import Document

log = get_logger(__name__)

UNKNOWN = "unknown"
PROMPT_VERSION = "v1"
_SNIPPET_CHARS = 1200


class PageLabel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    page: int
    type: str


class ClassificationOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    labels: list[PageLabel] = Field(default_factory=list)


def _label_schema() -> dict[str, Any]:
    schema = ClassificationOutput.model_json_schema()
    schema.pop("title", None)
    return schema


async def classify_pages(
    document: Document,
    provider: ModelProvider,
    model_name: str,
    *,
    settings: Settings | None = None,
) -> dict[int, str]:
    """Label every page with a registered document type or `unknown`."""
    settings = settings or get_settings()
    if not document.has_text_layer:
        raise ClassificationError(
            "Cannot auto-detect document type: PDF has no text layer; pass --type explicitly"
        )

    template = load_prompt("classify", PROMPT_VERSION)
    schema = _label_schema()
    system_prompt, user_prompt = template.render(
        document_types="\n".join(
            f"- `{t.name}` — {t.title}: {t.description}" for t in list_document_types()
        ),
        schema_json=json.dumps(schema, indent=2),
        pages_text="\n\n".join(
            f"--- page {p.number} ---\n{p.text[:_SNIPPET_CHARS]}" for p in document.pages
        ),
    )
    request = ExtractionRequest(
        model=model_name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_schema=schema,
        document_type="classify",
        source_name=document.filename,
    )
    response = await provider.extract_structured(request)
    labels = _coerce_labels(_parse_labels(response.raw_json), len(document.pages))
    log.info(
        "classification_completed",
        model=response.model,
        known=sum(1 for t in labels.values() if t != UNKNOWN),
        unknown=sum(1 for t in labels.values() if t == UNKNOWN),
        ms=response.latency_ms,
    )
    return labels


def _parse_labels(raw_json: str) -> list[PageLabel]:
    try:
        return ClassificationOutput.model_validate(parse_json_output(raw_json)).labels
    except (ExtractionValidationError, ValidationError) as exc:
        raise ClassificationError(
            "Classifier output is not valid labels JSON",
            details={"error": str(exc)[:300]},
        ) from exc


def _coerce_labels(labels: list[PageLabel], page_count: int) -> dict[int, str]:
    result = {page: UNKNOWN for page in range(1, page_count + 1)}
    for label in labels:
        if 1 <= label.page <= page_count:
            result[label.page] = label.type if label.type in DOCUMENT_TYPES else UNKNOWN
    return result
