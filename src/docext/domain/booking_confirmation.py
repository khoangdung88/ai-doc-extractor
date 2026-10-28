"""Booking Confirmation schema (carrier / forwarder booking for a sea or air shipment)."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from pydantic import Field

from docext.domain.base import BaseDocumentSchema, DocumentType
from docext.domain.common import Party, Volume, Weight

TransportMode = Literal["sea", "air", "road", "rail"]

_MAWB_RE = re.compile(r"^\d{3}-\d{8}$")


class ContainerBooking(BaseDocumentSchema):
    container_type: str | None = Field(default=None, description="ISO size/type, e.g. 40HC")
    quantity: int | None = None
    pickup_depot: str | None = None
    return_terminal: str | None = None


class BookingConfirmation(BaseDocumentSchema):
    schema_version: str = "2"

    booking_number: str | None = Field(
        default=None,
        description="Booking / BKG number printed by the carrier or forwarder; for air "
        "bookings without one, the HAWB number",
    )
    booking_reference: str | None = Field(
        default=None,
        description="Shipper's own reference quoted on the booking (invoice, PO or contract no.)",
    )
    booking_date: date | None = None
    transport_mode: TransportMode | None = None
    carrier: Party | None = Field(
        default=None, description="Shipping line or airline operating the transport"
    )
    forwarder: Party | None = Field(
        default=None, description="Freight forwarder / agent issuing the confirmation"
    )
    shipper: Party | None = None
    consignee: Party | None = None

    # Sea
    vessel: str | None = None
    voyage: str | None = None
    containers: list[ContainerBooking] = Field(default_factory=list)

    # Air
    mawb_number: str | None = Field(default=None, description="Master air waybill, NNN-NNNNNNNN")
    hawb_number: str | None = Field(default=None, description="House air waybill")
    flight_number: str | None = Field(default=None, description="e.g. VN611")

    place_of_receipt: str | None = None
    port_of_loading: str | None = Field(default=None, description="Port or airport of departure")
    port_of_discharge: str | None = Field(default=None, description="Port or airport of arrival")
    place_of_delivery: str | None = None
    etd: date | None = None
    eta: date | None = None
    ex_factory_date: date | None = None

    si_cutoff: datetime | None = Field(default=None, description="Shipping instruction cut-off")
    vgm_cutoff: datetime | None = None
    cy_cutoff: datetime | None = Field(default=None, description="Container yard cut-off (sea)")
    cargo_cutoff: datetime | None = Field(
        default=None, description="Cargo / warehouse handover cut-off (air or unspecified)"
    )
    terminal: str | None = Field(
        default=None, description="Handling terminal / warehouse where cargo is delivered"
    )

    pieces: int | None = Field(default=None, description="Number of packages booked")
    commodity: str | None = None
    gross_weight: Weight | None = None
    chargeable_weight: Weight | None = None
    volume: Volume | None = None
    service_contract: str | None = None
    remarks: str | None = None

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.etd and self.eta and self.eta < self.etd:
            warnings.append("eta is before etd")
        if not (self.booking_number or self.hawb_number or self.mawb_number):
            warnings.append("booking_number missing")
        if self.mawb_number and not _MAWB_RE.match(self.mawb_number):
            warnings.append("mawb_number is not in NNN-NNNNNNNN format")
        if self.transport_mode == "air" and self.containers:
            warnings.append("containers listed on an air booking")
        if self.transport_mode == "sea" and (
            self.mawb_number or self.hawb_number or self.flight_number
        ):
            warnings.append("air waybill / flight on a sea booking")
        return warnings


BOOKING_CONFIRMATION_TYPE = DocumentType(
    name="booking_confirmation",
    title="Booking Confirmation",
    schema=BookingConfirmation,
    prompt_version="v2",
    description=(
        "Carrier/forwarder confirmation (sea or air): booking no, vessel/voyage or "
        "MAWB/HAWB/flight, "
        "ports or airports, ETD/ETA, cut-offs, containers or pieces."
    ),
)
