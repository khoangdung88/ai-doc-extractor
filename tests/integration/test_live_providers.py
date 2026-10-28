"""Live provider smoke tests. Skipped unless the vendor key is set. Run: pytest -m integration."""

from __future__ import annotations

import os

import pytest

from docext.extraction.pipeline import extract
from docext.ingestion.base import Document, Page

pytestmark = pytest.mark.integration

INVOICE_TEXT = """COMMERCIAL INVOICE
Invoice No.: INV-2026-0001        Date: 2026-03-02
Seller: ACME EXPORT CO., LTD, 1 Example Road, Ho Chi Minh City, Vietnam
Buyer: SAMPLE IMPORTS GMBH, 2 Beispielstrasse, Hamburg, Germany
Incoterm: FOB HO CHI MINH        Currency: USD
1  Wooden chairs   HS 940161   100 PCS  @ 25.00   2,500.00
2  Wooden tables   HS 940360    20 PCS  @ 150.00  3,000.00
TOTAL: USD 5,500.00
"""


@pytest.mark.parametrize(
    ("env_var", "model"),
    [
        ("OPENAI_API_KEY", "openai:gpt-4o-mini"),
        ("ANTHROPIC_API_KEY", "anthropic:claude-3-5-haiku-latest"),
    ],
)
async def test_live_invoice_extraction(env_var: str, model: str) -> None:
    if not os.environ.get(env_var):
        pytest.skip(f"{env_var} not set")
    document = Document(
        filename="synthetic.txt", mime_type="text/plain", pages=[Page(number=1, text=INVOICE_TEXT)]
    )

    result = await extract(document, "invoice", model)

    assert result.data["invoice_number"] == "INV-2026-0001"
    assert result.data["total_amount"]["amount"] in ("5500.00", "5500", "5500.0")
    assert len(result.data["line_items"]) == 2
