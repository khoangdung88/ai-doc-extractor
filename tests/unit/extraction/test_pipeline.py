import pytest

from docext.core.config import Settings
from docext.core.errors import (
    ExtractionValidationError,
    InputTooLargeError,
    UnknownProviderError,
)
from docext.extraction.pipeline import extract
from docext.extraction.providers.mock import MockProvider
from docext.ingestion.base import Document


async def test_extract_with_echo_returns_all_null_document(
    settings: Settings, text_document: Document
) -> None:
    result = await extract(text_document, "invoice", "mock:echo", settings=settings)

    assert result.document_type == "invoice"
    assert result.model == "mock:echo"
    assert result.prompt_version == "v2"
    assert result.data["invoice_number"] is None
    assert "invoice_number missing" in result.warnings
    assert result.pages == 1


async def test_extract_prompt_contains_schema_and_document_text(
    settings: Settings, text_document: Document
) -> None:
    provider = MockProvider(settings)

    await extract(text_document, "invoice", "mock:echo", settings=settings, provider=provider)

    request = provider.requests[0]
    assert request.document_type == "invoice"
    assert "INV-001" in request.user_prompt
    assert '"invoice_number"' in request.user_prompt
    assert request.json_schema["type"] == "object"


async def test_extract_validates_canned_output(settings: Settings, text_document: Document) -> None:
    provider = MockProvider(
        settings,
        canned={
            "invoice_number": "INV-001",
            "total_amount": {"amount": "100.00", "currency": "USD"},
        },
    )

    result = await extract(
        text_document, "invoice", "mock:canned", settings=settings, provider=provider
    )

    assert result.data["invoice_number"] == "INV-001"
    assert result.data["total_amount"] == {"amount": "100.00", "currency": "USD"}
    assert result.warnings == []


async def test_extract_rejects_schema_mismatch(settings: Settings, text_document: Document) -> None:
    provider = MockProvider(settings, canned={"line_items": "not a list"})

    with pytest.raises(ExtractionValidationError) as exc:
        await extract(text_document, "invoice", "mock:canned", settings=settings, provider=provider)

    assert exc.value.details["errors"]


async def test_extract_uses_default_model_when_none_given(
    settings: Settings, text_document: Document
) -> None:
    result = await extract(text_document, "packing_list", None, settings=settings)

    assert result.model == "mock:echo"


async def test_extract_rejects_bad_model_spec(settings: Settings, text_document: Document) -> None:
    with pytest.raises(UnknownProviderError):
        await extract(text_document, "invoice", "gpt-4o", settings=settings)


async def test_extract_rejects_oversized_text(settings: Settings, text_document: Document) -> None:
    small = settings.model_copy(update={"max_input_chars": 10})

    with pytest.raises(InputTooLargeError):
        await extract(text_document, "invoice", "mock:echo", settings=small)
