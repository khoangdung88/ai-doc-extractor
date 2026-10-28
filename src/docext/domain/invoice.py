"""Commercial Invoice schema (incl. processing-trade invoices with several price columns)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import Field, model_validator

from docext.domain.base import BaseDocumentSchema, DocumentType
from docext.domain.common import LineItem, Money, Party, PriceComponent, Quantity, Weight

_ABS_TOLERANCE = Decimal("0.01")
_REL_TOLERANCE = Decimal("0.005")


def _consistent(quantity: Quantity, unit_price: Money, amount: Money) -> bool:
    expected = quantity.value * unit_price.amount
    tolerance = max(_ABS_TOLERANCE, abs(expected) * _REL_TOLERANCE)
    return abs(expected - amount.amount) <= tolerance


class Invoice(BaseDocumentSchema):
    schema_version: str = "2"

    invoice_number: str | None = None
    invoice_date: date | None = None
    contract_number: str | None = Field(
        default=None, description="Sales / processing contract or PO number quoted on the invoice"
    )
    seller: Party | None = None
    buyer: Party | None = Field(default=None, description="'Sold to' / 'Bill to' party")
    consignee: Party | None = Field(default=None, description="'Shipped to' party, if different")
    currency: str | None = Field(default=None, description="Document currency, ISO-4217")
    incoterm: str | None = Field(default=None, description="3-letter code, e.g. FOB")
    incoterm_place: str | None = None
    payment_terms: str | None = None
    shipped_per: str | None = Field(
        default=None, description="Mode or vessel/flight as printed, e.g. 'AIR FREIGHT'"
    )
    shipment_date: date | None = Field(default=None, description="'Ship on board' / ETD date")
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    country_of_origin: str | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: Money | None = None
    freight: Money | None = None
    insurance: Money | None = None
    discount: Money | None = None
    total_amount: Money | None = Field(default=None, description="'Total invoice amount'")
    amount_components: list[PriceComponent] = Field(
        default_factory=list,
        description="Other printed totals (e.g. processing-fee total) besides total_amount",
    )
    total_quantity: Decimal | None = None
    total_packages: int | None = None
    net_weight: Weight | None = None
    gross_weight: Weight | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _reconcile_prices_from_components(self) -> Invoice:
        """Deterministic repair: when a line's `unit_price` does not explain `amount` but one of its
        printed price columns does, take that column. Models often paste a column total into
        `unit_price` on multi-column (processing-trade) invoices."""
        for item in self.line_items:
            if item.quantity is None or not item.price_components:
                continue
            if (
                item.unit_price
                and item.amount
                and _consistent(item.quantity, item.unit_price, item.amount)
            ):
                continue
            candidates = [
                c
                for c in item.price_components
                if c.unit_price and c.amount and _consistent(item.quantity, c.unit_price, c.amount)
            ]
            if not candidates:
                continue
            chosen = next(
                (c for c in candidates if item.amount and c.amount == item.amount),
                next(
                    (c for c in candidates if self.total_amount and c.amount == self.total_amount),
                    candidates[-1],
                ),
            )
            item.unit_price, item.amount = chosen.unit_price, chosen.amount
        return self

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        for item in self.line_items:
            if item.quantity is None or item.unit_price is None or item.amount is None:
                continue
            if not _consistent(item.quantity, item.unit_price, item.amount):
                warnings.append(
                    f"line {item.line_no}: quantity x unit_price = "
                    f"{item.quantity.value * item.unit_price.amount} differs from "
                    f"amount {item.amount.amount}"
                )
        amounts = [li.amount.amount for li in self.line_items if li.amount is not None]
        if amounts and self.total_amount is not None and self.subtotal is None:
            line_sum = sum(amounts, Decimal(0))
            if abs(line_sum - self.total_amount.amount) > _ABS_TOLERANCE:
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
    prompt_version="v3",
    description=(
        "Seller-to-buyer invoice for exported goods: parties, line items (incl. multi-column "
        "prices), totals, terms, shipment details."
    ),
)
