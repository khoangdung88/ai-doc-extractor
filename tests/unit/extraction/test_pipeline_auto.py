import json
from typing import Any

from docext.core.config import Settings
from docext.extraction.pipeline import extract_auto
from docext.extraction.providers.base import (
    ExtractionRequest,
    ProviderCapabilities,
    ProviderResponse,
)
from docext.extraction.providers.mock import MockProvider
from docext.ingestion.base import Document, Page


class _PerTypeMock(MockProvider):
    """Mock that returns a different canned payload per `request.document_type`."""

    def __init__(self, settings: Settings, payloads: dict[str, dict[str, Any]]) -> None:
        super().__init__(settings)
        self._payloads = payloads

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities()

    async def extract_structured(self, request: ExtractionRequest) -> ProviderResponse:
        self.requests.append(request)
        return ProviderResponse(
            raw_json=json.dumps(self._payloads.get(request.document_type, {})),
            model=f"mock:{request.model}",
        )


def _combined_document() -> Document:
    return Document(
        filename="combined.pdf",
        mime_type="application/pdf",
        pages=[
            Page(number=1, text="COMMERCIAL INVOICE INV-001"),
            Page(number=2, text="PACKING LIST PL-9"),
            Page(number=3, text="Dear customer, please find attached..."),
        ],
    )


async def test_extract_auto_detects_types_and_skips_unknown(settings: Settings) -> None:
    provider = _PerTypeMock(
        settings,
        {
            "classify": {
                "labels": [
                    {"page": 1, "type": "invoice"},
                    {"page": 2, "type": "packing_list"},
                    {"page": 3, "type": "unknown"},
                ]
            },
            "invoice": {"invoice_number": "INV-001"},
            "packing_list": {"packing_list_number": "PL-9"},
        },
    )

    result = await extract_auto(
        _combined_document(), "mock:canned", settings=settings, provider=provider
    )

    assert [r.document_type for r in result.results] == ["invoice", "packing_list"]
    assert [r.pages for r in result.results] == [1, 1]
    assert result.results[0].data["invoice_number"] == "INV-001"
    assert result.skipped_pages[0].pages == [3]
    # one provider reused: 1 classify + 2 extract calls
    assert [r.document_type for r in provider.requests] == [
        "classify",
        "invoice",
        "packing_list",
    ]


async def test_extract_auto_merges_same_type_pages(settings: Settings) -> None:
    provider = _PerTypeMock(
        settings,
        {
            "classify": {
                "labels": [
                    {"page": 1, "type": "invoice"},
                    {"page": 2, "type": "unknown"},
                    {"page": 3, "type": "invoice"},
                ]
            },
            "invoice": {"invoice_number": "INV-001"},
        },
    )

    result = await extract_auto(
        _combined_document(), "mock:canned", settings=settings, provider=provider
    )

    assert len(result.results) == 1
    assert result.results[0].document_type == "invoice"
    assert result.results[0].pages == 2
    invoice_prompt = provider.requests[1].user_prompt
    # merged pages 1+3 are sent; the unknown page 2 is not
    assert "INV-001" in invoice_prompt
    assert "Dear customer" in invoice_prompt
    assert "PL-9" not in invoice_prompt


async def test_extract_auto_all_unknown_returns_empty_results(settings: Settings) -> None:
    provider = _PerTypeMock(settings, {"classify": {"labels": []}})

    result = await extract_auto(
        _combined_document(), "mock:canned", settings=settings, provider=provider
    )

    assert result.results == []
    assert result.skipped_pages[0].pages == [1, 2, 3]
    assert len(provider.requests) == 1
