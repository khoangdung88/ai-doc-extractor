"""Shared fixtures. Keep minimal; test-specific setup belongs in the test module."""

from __future__ import annotations

from pathlib import Path

import pytest

from docext.core.config import Settings
from docext.ingestion.base import Document, Page

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        default_model="mock:echo",
        mock_fixture_dir=FIXTURES / "golden",
    )


@pytest.fixture
def text_document() -> Document:
    return Document(
        filename="sample_invoice.pdf",
        mime_type="application/pdf",
        pages=[Page(number=1, text="INVOICE No. INV-001\nTotal: USD 100.00")],
    )


def make_pdf(lines: list[str]) -> bytes:
    """Build a tiny single-page PDF with the given text lines (synthetic, no real data)."""
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    y = 72
    for line in lines:
        page.insert_text((72, y), line, fontsize=11)
        y += 16
    data: bytes = doc.tobytes()
    doc.close()
    return data
