import pytest
from tests.conftest import make_pdf

from docext.core.errors import DocumentLoadError, UnsupportedFormatError
from docext.ingestion.pdf import PdfLoader
from docext.ingestion.registry import load_document


async def test_pdf_loader_extracts_text_per_page() -> None:
    data = make_pdf(["INVOICE No. INV-001", "Total: USD 100.00"])

    document = await PdfLoader().load(data, "a.pdf")

    assert document.mime_type == "application/pdf"
    assert len(document.pages) == 1
    assert "INV-001" in document.pages[0].text
    assert document.metadata["has_text_layer"] is True
    assert "--- page 1 ---" in document.text


async def test_pdf_loader_can_render_page_images() -> None:
    document = await PdfLoader(render_images=True, render_dpi=36).load(make_pdf(["x"]))

    assert document.pages[0].image_png is not None
    assert document.pages[0].image_png.startswith(b"\x89PNG")


async def test_pdf_loader_rejects_garbage() -> None:
    with pytest.raises(DocumentLoadError):
        await PdfLoader().load(b"%PDF-garbage")


async def test_load_document_rejects_unknown_format() -> None:
    with pytest.raises(UnsupportedFormatError):
        await load_document(b"plain text", "a.txt")
