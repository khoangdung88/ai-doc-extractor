"""Golden tests: fixture PDF → mock:fixture provider → validates and round-trips the golden JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.conftest import FIXTURES

from docext.core.config import Settings
from docext.domain.registry import get_document_type
from docext.extraction.pipeline import extract
from docext.ingestion.registry import load_document

GOLDEN = sorted((FIXTURES / "golden").glob("*/*.json"))


@pytest.mark.parametrize("golden_path", GOLDEN, ids=lambda p: f"{p.parent.name}/{p.stem}")
async def test_golden_output_validates_against_schema(
    golden_path: Path, settings: Settings
) -> None:
    doc_type = golden_path.parent.name
    pdf_path = FIXTURES / "documents" / doc_type / f"{golden_path.stem}.pdf"
    document = await load_document(pdf_path.read_bytes(), pdf_path.name, settings=settings)

    result = await extract(document, doc_type, "mock:fixture", settings=settings)

    schema = get_document_type(doc_type).schema
    expected = schema.model_validate(json.loads(golden_path.read_text())).model_dump(mode="json")
    for field, value in expected.items():
        assert result.data[field] == value, field
    assert result.warnings == []
    assert document.has_text_layer
