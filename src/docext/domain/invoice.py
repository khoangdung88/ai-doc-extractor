"""Commercial Invoice schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import Field

from docext.domain.base import BaseDocumentSchema, DocumentType
from docext.domain.common import LineItem, Money, Party


class Invoice(BaseDocumentSchema):
    invoice_number: str | None = None
    invoice_date: date | None = None
    seller: Party | None = None
    buyer: Party | None = None
    consignee: Party | None = Field(default=None, description="If different from buyer")
    currency: str | None = Field(default=None, description="Document currency, ISO-4217")
    incoterm: str | None = Field(default=None, description="3-letter code, e.g. FOB")
    incoterm_place: str | None = None
    payment_terms: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    country_of_origin: str | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: Money | None = None
    freight: Money | None = None
    insurance: Money | None = None
    discount: Money | None = None
    total_amount: Money | None = None
    total_quantity: Decimal | None = None
    notes: str | None = None

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        amounts = [li.amount.amount for li in self.line_items if li.amount is not None]
        if amounts and self.total_amount is not None and self.subtotal is None:
            line_sum = sum(amounts, Decimal(0))
            if abs(line_sum - self.total_amount.amount) > Decimal("0.01"):
                warnings.append(
                    f"line_items sum {line_sum} differs from total_amount "
                    f"{self.total_amount.amount}"
                )
        if not self.invoice_number:
            warnings.append("invoice_number missing")
        return warnings


INVOICE_TYPE = DocumentType(
    name="invoice",
    title="Commercial Invoice",
    schema=Invoice,
    prompt_version="v1",
    description="Seller-to-buyer invoice for exported goods: parties, line items, totals, terms.",
)
