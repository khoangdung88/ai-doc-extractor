"""Value objects reused across document schemas. Add here only if genuinely generic."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Value(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class Party(_Value):
    name: str | None = None
    address: str | None = None
    country: str | None = Field(default=None, description="ISO-3166 alpha-2 if determinable")
    tax_id: str | None = None
    contact: str | None = Field(default=None, description="Phone / email / attention line")


class Money(_Value):
    amount: Decimal
    currency: str | None = Field(default=None, description="ISO-4217 code, e.g. USD")


class Quantity(_Value):
    value: Decimal
    unit: str | None = Field(default=None, description="e.g. PCS, SET, KG, CTN")


class Weight(_Value):
    value: Decimal
    unit: str = Field(default="KG", description="KG or LB")


class Volume(_Value):
    value: Decimal
    unit: str = Field(default="CBM", description="CBM or CFT")


class PriceComponent(_Value):
    """One priced column of a line when an invoice prints several (processing fee, material)."""

    label: str = Field(description="Column heading as printed, e.g. 'Processing fee'")
    unit_price: Money | None = None
    amount: Money | None = None


class LineItem(_Value):
    line_no: int | None = None
    description: str | None = None
    part_number: str | None = Field(default=None, description="Item / part / model code as printed")
    hs_code: str | None = Field(default=None, description="Digits only, 6-10 chars")
    origin_country: str | None = None
    quantity: Quantity | None = None
    unit_price: Money | None = Field(
        default=None, description="Per-unit price of the column that adds up to the invoice total"
    )
    amount: Money | None = Field(default=None, description="Line total = quantity x unit_price")
    price_components: list[PriceComponent] = Field(
        default_factory=list,
        description="Every priced column when the invoice prints more than one; empty otherwise",
    )

    @field_validator("hs_code", mode="before")
    @classmethod
    def _digits_only_hs_code(cls, value: object) -> str | None:
        """Keep digits only; drop values that cannot be an HS code (e.g. a pasted quantity)."""
        if value is None:
            return None
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        return digits if 6 <= len(digits) <= 10 else None


class DateRange(_Value):
    start: date | None = None
    end: date | None = None
