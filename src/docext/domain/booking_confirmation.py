"""Booking Confirmation schema (carrier / forwarder booking for a sea shipment)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from docext.domain.base import BaseDocumentSchema, DocumentType
from docext.domain.common import Party, Volume, Weight


class ContainerBooking(BaseDocumentSchema):
    container_type: str | None = Field(default=None, description="ISO size/type, e.g. 40HC")
    quantity: int | None = None
    pickup_depot: str | None = None
    return_terminal: str | None = None


class BookingConfirmation(BaseDocumentSchema):
    booking_number: str | None = None
    booking_date: date | None = None
    carrier: Party | None = None
    forwarder: Party | None = None
    shipper: Party | None = None
    consignee: Party | None = None
    vessel: str | None = None
    voyage: str | None = None
    place_of_receipt: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    place_of_delivery: str | None = None
    etd: date | None = None
    eta: date | None = None
    si_cutoff: datetime | None = Field(default=None, description="Shipping instruction cut-off")
    vgm_cutoff: datetime | None = None
    cy_cutoff: datetime | None = Field(default=None, description="Container yard / cargo cut-off")
    containers: list[ContainerBooking] = Field(default_factory=list)
    commodity: str | None = None
    gross_weight: Weight | None = None
    volume: Volume | None = None
    service_contract: str | None = None
    remarks: str | None = None

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.etd and self.eta and self.eta < self.etd:
            warnings.append("eta is before etd")
        if not self.booking_number:
            warnings.append("booking_number missing")
        return warnings


BOOKING_CONFIRMATION_TYPE = DocumentType(
    name="booking_confirmation",
    title="Booking Confirmation",
    schema=BookingConfirmation,
    prompt_version="v1",
    description=(
        "Carrier/forwarder confirmation: booking no, vessel/voyage, ports, ETD/ETA, cut-offs, "
        "containers."
    ),
)
