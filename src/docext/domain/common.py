"""Value objects reused across document schemas. Add here only if genuinely generic."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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


class LineItem(_Value):
    line_no: int | None = None
    description: str | None = None
    hs_code: str | None = Field(default=None, description="Digits only, 6-10 chars")
    origin_country: str | None = None
    quantity: Quantity | None = None
    unit_price: Money | None = None
    amount: Money | None = None


class DateRange(_Value):
    start: date | None = None
    end: date | None = None
