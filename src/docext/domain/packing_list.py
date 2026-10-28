"""Packing List schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import Field

from docext.domain.base import BaseDocumentSchema, DocumentType
from docext.domain.common import Party, Quantity, Volume, Weight


class Package(BaseDocumentSchema):
    package_no: str | None = Field(default=None, description="e.g. '1-10' or 'CTN 5'")
    package_type: str | None = Field(default=None, description="CTN, PLT, BAG, ...")
    description: str | None = None
    hs_code: str | None = None
    quantity: Quantity | None = None
    net_weight: Weight | None = None
    gross_weight: Weight | None = None
    dimensions_cm: str | None = Field(default=None, description="LxWxH in cm as written")
    volume: Volume | None = None


class PackingList(BaseDocumentSchema):
    packing_list_number: str | None = None
    invoice_number: str | None = Field(default=None, description="Related invoice, if referenced")
    issue_date: date | None = None
    shipper: Party | None = None
    consignee: Party | None = None
    notify_party: Party | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    vessel: str | None = None
    voyage: str | None = None
    container_numbers: list[str] = Field(default_factory=list)
    marks_and_numbers: str | None = None
    packages: list[Package] = Field(default_factory=list)
    total_packages: Decimal | None = None
    total_quantity: Quantity | None = None
    total_net_weight: Weight | None = None
    total_gross_weight: Weight | None = None
    total_volume: Volume | None = None

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        if (
            self.total_gross_weight
            and self.total_net_weight
            and self.total_gross_weight.value < self.total_net_weight.value
        ):
            warnings.append("total_gross_weight is lower than total_net_weight")
        if not self.packages:
            warnings.append("no packages extracted")
        return warnings


PACKING_LIST_TYPE = DocumentType(
    name="packing_list",
    title="Packing List",
    schema=PackingList,
    prompt_version="v1",
    description="How goods are packed: packages, marks, net/gross weights, dimensions, volumes.",
)
