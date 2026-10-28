import pytest

from docext.core.config import Settings
from docext.core.errors import ClassificationError
from docext.extraction.classification import classify_pages
from docext.extraction.providers.mock import MockProvider
from docext.ingestion.base import Document, Page


def _document(pages: list[tuple[int, str]]) -> Document:
    return Document(
        filename="combined.pdf",
        mime_type="application/pdf",
        pages=[Page(number=n, text=t) for n, t in pages],
    )


async def test_classify_labels_every_page(settings: Settings) -> None:
    provider = MockProvider(
        settings,
        canned={
            "labels": [
                {"page": 1, "type": "invoice"},
                {"page": 2, "type": "packing_list"},
                {"page": 3, "type": "unknown"},
            ]
        },
    )

    labels = await classify_pages(
        _document([(1, "INVOICE"), (2, "PACKING LIST"), (3, "cover letter")]),
        provider,
        "canned",
        settings=settings,
    )

    assert labels == {1: "invoice", 2: "packing_list", 3: "unknown"}
    request = provider.requests[0]
    assert request.document_type == "classify"
    assert "--- page 1 ---" in request.user_prompt
    assert "`invoice`" in request.user_prompt


async def test_classify_coerces_untrusted_output(settings: Settings) -> None:
    provider = MockProvider(
        settings,
        canned={
            "labels": [
                {"page": 1, "type": "not_a_real_type"},
                {"page": 99, "type": "invoice"},
                {"page": "2", "type": "invoice", "extra": "ignored"},
            ]
        },
    )

    labels = await classify_pages(
        _document([(1, "a"), (2, "b"), (3, "c")]), provider, "canned", settings=settings
    )

    # unregistered type -> unknown; out-of-range page dropped; missing page -> unknown
    assert labels == {1: "unknown", 2: "invoice", 3: "unknown"}


async def test_classify_rejects_document_without_text(settings: Settings) -> None:
    provider = MockProvider(settings, canned={"labels": []})

    with pytest.raises(ClassificationError, match="no text layer"):
        await classify_pages(
            _document([(1, "   "), (2, "")]), provider, "canned", settings=settings
        )


async def test_classify_rejects_malformed_output(settings: Settings) -> None:
    provider = MockProvider(settings, canned={"labels": "not a list"})

    with pytest.raises(ClassificationError):
        await classify_pages(_document([(1, "x")]), provider, "canned", settings=settings)
